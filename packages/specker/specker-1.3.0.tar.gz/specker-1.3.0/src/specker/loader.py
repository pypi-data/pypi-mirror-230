# Copyright 2023-2023 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Specker JSON Specification Validator,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import os
import re
import json
import typing
import logging
from pathlib import Path

# from specker import content

if __name__ == "loader":
    # pylint: disable=import-error
    from content import SpecContent
    # pylint: enable=import-error
else:
    from .content import SpecContent

class SpecLoader:
    """Spec Loader and Handler
    """
    _specs:dict[str,dict[str,SpecContent]]
    _output:list[str]
    logger:logging.Logger

    @property
    def spec_names(self) -> list[str]:
        """Property: Spec Names
        @retval list[str] List of loaded Spec Names
        """
        return list(self._specs.keys())

    def __init__(self,spec_root:Path,debug:bool = False) -> None:
        """Initializer
        @param Path \c spec_root Location where .spec files are located
        @param bool \c debug Enable logging.DEBUG (logging.ERROR if False)
        """
        self.logger = logging.getLogger("specker.loader.SpecLoader")
        self.logger.setLevel(logging.ERROR)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        self._specs = {}

        specs_raw:dict[str,typing.Any] = {}
        spec_name:str = ""
        spec:dict[str,typing.Any] = {}

        self._output:list[str] = [
            "# Configuration Options",
            "Auto generated from .spec files"
        ]

        # pylint: disable=unused-variable
        for root, subdirs, files in os.walk(spec_root.resolve().as_posix()):
            spec_path:Path = Path(root).resolve()
            for file in files:
                if not file.endswith(".spec"):
                    continue
                self.logger.debug(f"Loading: {file}")
                try:
                    with open(spec_path.joinpath(file), "r", encoding="utf-8") as f:
                        spec = json.loads(f.read())
                except BaseException as e:
                    self.logger.error(f"Failed loading: {file}, {e}")
                    self.logger.debug(e,exc_info=True)
                    continue
                spec_name = re.sub(r'\.spec',"",file)
                specs_raw[spec_name] = spec
        for spec_file_name,spec_data in specs_raw.items():
            self._specs[spec_file_name] = {}
            for spec_name,spec in spec_data.items():
                spec["name"] = spec_name
                self._specs[spec_file_name][spec_name] = SpecContent(spec)
        # pylint: enable=unused-variable

    def compare(self,spec_file_name:str,content:dict[str,typing.Any]) -> bool:
        """Compare a Spec against Content
        @param str \c spec_file_name Spec File Name to pull
        @param dict[str,typing.Any] \c content Content to compare against Spec
        @retval bool Whether Check passed successfully
        """
        spec_items:dict[str,SpecContent] = self.get(spec_file_name)
        if len(spec_items) == 0:
            self.logger.warning(f"Spec Items for {spec_file_name} was empty for content")
            return True
        if "__any_item__" in spec_items.keys():
            self.logger.debug("Jumping to Any Item Compare")
            return self._compare_item_items(spec_items["__any_item__"],content)
        self.logger.debug("Jumping to Defined Item Compare")
        return self._compare_defined_items(spec_items,content)

    def _compare_defined_items(self,spec_items:dict[str,SpecContent],content:dict[str,typing.Any]) -> bool:
        """Defined Item Comparison. Validate each item of the spec against content[spec_item_name]
        @param dict[str,SpecContent] \c spec_items Dictionary of specs for content block to be compared against
        @param dict[str,Any] \c content Content to Compare
        @retval bool Success/Failure. Messages are logged to logging.Logger
        """
        spec_keys:list[str] = list(spec_items.keys())
        content_keys:list[str] = list(content.keys())
        spec_pass:bool = True
        check:bool
        for key in content.keys():
            if "__any_item__" in spec_keys:
                check = self._compare_item_items(spec_items["__any_item__"],content[key])
                if not check:
                    self.logger.error(f"{key}: fail, validation against __any_item__ failed")
                    spec_pass = False
                continue
            if key not in spec_keys:
                spec_pass = False
                self.logger.error(f"{key}: fail, invalid option")
                continue
        if not spec_pass:
            return False
        for key,spec_item in spec_items.items():
            if spec_item.get("name") not in content_keys and not spec_item.get("required"):
                self.logger.debug(f"{key} was not defined, using default value")
                content[key] = spec_item.get("default")
            elif spec_item.get("name") not in content_keys and spec_item.get("required"):
                spec_pass = False
                self.logger.error(f"{key}: fail, missing required option")
                continue
            if not spec_item.get("required") and content[key] is None:
                self.logger.debug(f"{key}: pass, not required, but is empty")
                continue
            check = self._compare_item_single(spec_item,key,content[key])
            if not check:
                spec_pass = False
        # spec_pass_str:str = "SUCCESS" if spec_pass else "FAIL"
        # self.logger.debug(f"__defined__ FINAL RESULT - {spec_pass_str}; {content}")
        return spec_pass

    def _compare_item_items(self,spec_item:SpecContent,content:typing.Union[dict[str,typing.Any],list[typing.Any]]) -> bool:
        """`__any_item__` Item Comparison. Validate each content item against spec_item, without regard for content key names
        @param SpecContent \c spec_item Spec to compare for each content item
        @param Union[dict[str,Any],list[Any] \c content Content to Compare
        @retval bool Success/Failure. Messages are logged to logging.Logger
        """
        spec_pass:bool = True
        content_keys:typing.Iterable
        if isinstance(content,list):
            content_keys = range(0,len(content))
        else:
            content_keys = content.keys()
        for key in content_keys:
            check:bool = self._compare_item_single(spec_item,key,content[key]) # type: ignore
            if not check:
                spec_pass = False
        # spec_pass_str:str = "SUCCESS" if spec_pass else "FAIL"
        # self.logger.debug(f"__item__    FINAL RESULT - {spec_pass_str}; {content}")
        return spec_pass

    def _compare_item_single(self,spec_item: SpecContent, key_name:typing.Union[str,int], value:typing.Any) -> bool:
        """Single Item Comparison. Compare content for value key against spec_item
        @param SpecContent \c spec_item Spec to compare to
        @param Any \c content Content to Compare
        @retval bool Success/Failure. Messages are logged to logging.Logger
        """
        spec_pass:bool = True
        if spec_item.type != type(value) and spec_item.type != typing.Any:
            spec_pass = False
            self.logger.error(f"{key_name}:_single_ fail, must be {str(spec_item.type)}, got: {str(type(value))}")
        else:
            self.logger.debug(f"{key_name}: pass, type match; need:{str(spec_item.type)}, got:{str(type(value))}")
        value_pass:bool = self._check_valid_values(spec_item=spec_item,content=value,key_name=key_name)
        if not value_pass:
            spec_pass = False
        if spec_item.get("spec_chain") is not None:
            spec_chain:str = spec_item.get("spec_chain")
            self.logger.debug(f"{key_name}: Contained Spec Chain, {spec_chain}. Checking")
            check:bool = self.compare(spec_chain,value)
            if not check:
                spec_pass = False
        return spec_pass

    def _check_valid_values(self,spec_item:SpecContent,content:typing.Any,key_name:typing.Union[str,int]) -> bool:
        """Verify if given value from content is in valid values of spec
        @param SpecContent \c spec_item Spec to Check against
        @param Any \c content Content to Validate
        @param str \c key_name Name of Key content came from, for logging output
        @retval bool Whether value is a valid value
        """
        valid_values:list[typing.Any] = spec_item.get("values")
        if len(valid_values) > 0:
            values:str = ""
            for v in valid_values:
                values += f",{str(v)}"
            values = values.lstrip(",")
            if content not in valid_values:
                self.logger.error(f"{key_name}: fail, invalid value '{content}'; must be one of: {values}")
                return False
            self.logger.debug(f"{key_name}: pass, value match, need:{values}, got:{str(content)}")
        return True

    def defaults(self,spec_file_name:str,parent_spec:typing.Union[SpecContent,None] = None) -> typing.Any:
        """Get any Defined Defaults from a Spec
        @param str \c spec_file_name Spec File Name to pull
        @param Union[SpecContent,None] \c parent_spec If following defaults from a parent, parent_spec is defined, and its type used to create the initial content entry for that item
        @retval dict[Any,Any] Spec Defaults
        """
        spec_file:dict[str,SpecContent] = self.get(spec_file_name)
        content:typing.Any
        if parent_spec is not None:
            content = (parent_spec.type)()
        else:
            content = {}

        for key_name,spec_item in spec_file.items():
            if key_name == "__any_item__":
                self.logger.debug("Skipping, Found Any Item entry")
                continue
            if spec_item.type == list:
                content[key_name] = []
            elif spec_item.type == dict:
                content[key_name] = {}
            else:
                content[key_name] = None
            try:
                content[key_name] = spec_item.get("default")
            except AttributeError:
                self.logger.debug(f"{key_name} did not have any defaults defined, ignoring")
                continue
            if spec_item.get("spec_chain") is not None:
                if spec_item.type in [ list, dict ]:
                    content[key_name] = self.defaults(spec_item.get("spec_chain"),spec_item)
        return content

    def get(self,spec_file_name:str) -> dict[str,SpecContent]:
        """Get Spec Content for a Config
        @param str \c spec_file_name Name of Spec to Get
        @retval dict[str,SpecContent] Configuration Spec
        """
        return self._specs[spec_file_name]

    def add(self,spec_file_name:str, spec_item:SpecContent) -> None:
        """Inject a partial Spec, without using a .spec file
        @param str \c spec_file_name Name of whole Spec to inject into
        @param SpecContent \c spec_item Spec Entry to Inject
        @retval None Nothing
        """
        if not spec_file_name in self._specs.keys():
            self._specs[spec_file_name] = {}
        spec_name:str = spec_item.get("name")
        self._specs[spec_file_name][spec_name] = spec_item

    def write(self,output_file:Path) -> None:
        """Write Loaded Specs to a Markdown file
        @param Path \c output_file Target File Path
        """

        for spec_file_name,spec_data in self._specs.items():
            self._output.append(f"## Spec for {spec_file_name}\n")
            for spec in spec_data.values():
                self._output.append(str(spec))

        output_path:Path = output_file.resolve()
        output_file_str:str = output_path.as_posix()
        self.logger.info(f"Writing to file {output_file_str}")
        with open(output_path,"w", encoding="utf-8") as f:
            f.write("\n".join(self._output))
