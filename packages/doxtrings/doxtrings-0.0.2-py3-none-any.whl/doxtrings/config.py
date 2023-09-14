"""
Defines the doXtrings configuration object and setter/getter functions
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Union

import tomli

from doxtrings.documentable import ALL_DOCUMENTABLE_TYPES, DocumentableType

_DEFAULT_CONFIG_FILES = (
    "pyproject.toml",
    "doxtrings.toml",
    ".doxtrings.toml",
    "doxtrings.json",
    ".doxtrings.json",
)

logger = logging.getLogger(__name__)


@dataclass
class IgnoreFilters:
    """
    Stores the ignore filters configuration.
    """

    ignore_prefixes_rules: Optional[List[str]] = None
    """
    A list of prefixes to Documentable's names that will mark them as ignored in the report.
    DEfaults to empty list.
    """
    include_prefixes_rules: Optional[List[str]] = None
    """
    A list of Documentable's name prefixes that will NOT be ignored in the report.
    Defaults to an empty list.
    """
    ignore_matches: Optional[List[str]] = None
    """
    A list of Documentable's names that will be ignored in the report.
    Defaults to empty list.
    """
    ignore_types: Optional[bool] = None
    """
    If set to True, will not require typing information in the docstring.
    Defaults to None. Prefer using `get_ignore_types` to get the value of this attribute,
    as it will account for `None` values.
    """
    ignore_args_and_kwargs: Optional[bool] = None
    """
    If set to True, will not require *args and **kwargs in the docstring.
    Defaults to None. Prefer using `get_ignore_args_and_kwargs` to get the value of this attribute,
    as it will account for `None` values.
    """

    def get_ignore_types(self) -> bool:
        """Gets ignore_types value. Defaults to False if ignore_types is None.

        Returns:
            bool: the ignore_types property or False if not set
        """
        return False if self.ignore_types is None else self.ignore_types

    def get_ignore_args_and_kwargs(self) -> bool:
        """Gets ignore_args_and_kwargs value. Defaults to False if ignore_args_and_kwargs is None.

        Returns:
            bool: the ignore_args_and_kwargs property or False if not set
        """
        return (
            False
            if self.ignore_args_and_kwargs is None
            else self.ignore_args_and_kwargs
        )

    @classmethod
    def merged(cls, base: IgnoreFilters, *mergeables: IgnoreFilters) -> IgnoreFilters:
        """
        Returns a merged version of the provided IgnoreFilters.
        Merge happens from left to right, meaning values in the leftmost filters will be
        overwritten by the rightmost ones.

        Args:
            base (IgnoreFilters): the base filter to be merged into the others.
            *mergeables (IgnoreFilters): the other filters to be merged.

        Returns:
            IgnoreFilters: the merged version of the filters.
        """
        merged = replace(base)
        for a in mergeables:
            if merged.ignore_prefixes_rules is None:
                merged.ignore_prefixes_rules = a.ignore_prefixes_rules
            if merged.include_prefixes_rules is None:
                merged.include_prefixes_rules = a.include_prefixes_rules
            if merged.ignore_matches is None:
                merged.ignore_matches = a.ignore_matches
            if merged.ignore_types is None:
                merged.ignore_types = a.ignore_types
            if merged.ignore_args_and_kwargs is None:
                merged.ignore_args_and_kwargs = a.ignore_args_and_kwargs
        return merged


@dataclass
class IgnoreFiltersRules:
    """
    A series of IgnoreFilters to be applied to specific types.
    """

    default: IgnoreFilters = field(default_factory=lambda: IgnoreFilters())
    """Ignore Filters for all documentables"""
    callables: IgnoreFilters = field(default_factory=lambda: IgnoreFilters())
    """Ignore Filters for all callables (functions and methods)"""
    functions: IgnoreFilters = field(default_factory=lambda: IgnoreFilters())
    """Ignore Filters for all functions"""
    methods: IgnoreFilters = field(default_factory=lambda: IgnoreFilters())
    """Ignore Filters for all methods"""
    classes: IgnoreFilters = field(default_factory=lambda: IgnoreFilters())
    """Ignore Filters for classes"""
    modules: IgnoreFilters = field(default_factory=lambda: IgnoreFilters())
    """Ignore Filters for modules"""
    assignments: IgnoreFilters = field(default_factory=lambda: IgnoreFilters())
    """Ignore Filters for all assignments (attributes, constants and variables)"""
    attributes: IgnoreFilters = field(default_factory=lambda: IgnoreFilters())
    """Ignore Filters for attributes"""
    constants: IgnoreFilters = field(default_factory=lambda: IgnoreFilters())
    """Ignore Filters for constants"""
    variables: IgnoreFilters = field(default_factory=lambda: IgnoreFilters())
    """Ignore Filters for variables"""


@dataclass
class DoXtringsConfig:
    """
    Class that stores all DoXtrings configuration.
    """

    root_dir: str = "./"
    """
    The root directory from where doxtrings will run the scan. Defaults to the current directory.
    """
    exclude_files: List[str] = field(
        default_factory=lambda: ["env", "venv", ".env", ".venv", "test/"]
    )
    """
    A list of files or directories to be excluded from the scan.
    Defaults to `["env", "venv", ".env", ".venv", "test/"]`
    """
    include_file_extensions: List[str] = field(default_factory=lambda: [".py"])
    """
    A list of file extensions that will be scanned.
    Defaults to `[".py"]`
    """
    types_to_check: List[str] = field(
        default_factory=lambda: list(ALL_DOCUMENTABLE_TYPES)
    )
    """
    A list with the types of Documentables that will be reported. Defaults to the list of all
    the available types (doxtrings.documentable:ALL_DOCUMENTABLE_TYPES)
    """
    docstring_format: str = "google"
    """
    The docstring format to use when parsing the docstring data. Possible values are "google",
    "epydoc", "rest" or "numpydoc". Defaults to "google".
    """

    parsing_depth: int = 2
    """
    How deep into the AST doxtrings will scan. Default value is 2.
    Using value of depth 2 means it will scan the root of a module and the first level of nesting,
    allowing for methods and attributes in classes to be scanned.
    """
    fail_fast: bool = False
    """If set to `True`, the scan will stop at the first difference found. Defaults to `False`"""

    fail_ignored_if_incorrect: bool = True
    """
    If set to `True`, documentables marked as ignored will still be added to the report if their
    docstring is not missing but is incorrect. Ignored types will also be added if incorrect.
    Defaults to `True`.
    """

    ignore_filters: IgnoreFiltersRules = field(
        default_factory=lambda: IgnoreFiltersRules()
    )
    """
    A dictionary of ignore rules specific for each type of documentable where the keys are the
    documentable types and the values are the specific rules. If any rule is specified
    it will override the default ignore rules for that type of documentable.
    """

    def get_ignore_filters(self, type: Union[DocumentableType, str]) -> IgnoreFilters:
        """Gets the ignore filters based on the type of documentable

        Args:
            type (Union[DocumentableType, str]): the type of documentable

        Raises:
            ValueError: If `type` is not a valid documentable type

        Returns:
            IgnoreFilters: Returns the ignore filters for the specific type
        """
        if type not in ALL_DOCUMENTABLE_TYPES:
            raise ValueError(
                f"Cannot get ignore filter for {type}. Valid types are {ALL_DOCUMENTABLE_TYPES}"
            )
        type_str = type.value if isinstance(type, DocumentableType) else type
        if type_str == DocumentableType.FUNCTION.value:
            return IgnoreFilters.merged(
                self.ignore_filters.functions,
                self.ignore_filters.callables,
                self.ignore_filters.default,
            )
        elif type_str == DocumentableType.METHOD.value:
            return IgnoreFilters.merged(
                self.ignore_filters.methods,
                self.ignore_filters.callables,
                self.ignore_filters.default,
            )
        elif type_str == DocumentableType.CLASS.value:
            return IgnoreFilters.merged(
                self.ignore_filters.classes, self.ignore_filters.default
            )
        elif type_str == DocumentableType.MODULE.value:
            return IgnoreFilters.merged(
                self.ignore_filters.modules, self.ignore_filters.default
            )
        elif type_str == DocumentableType.ATTRIBUTE.value:
            return IgnoreFilters.merged(
                self.ignore_filters.attributes,
                self.ignore_filters.assignments,
                self.ignore_filters.default,
            )
        elif type_str == DocumentableType.VARIABLE.value:
            return IgnoreFilters.merged(
                self.ignore_filters.variables,
                self.ignore_filters.assignments,
                self.ignore_filters.default,
            )
        elif type_str == DocumentableType.CONSTANT.value:
            return IgnoreFilters.merged(
                self.ignore_filters.constants,
                self.ignore_filters.assignments,
                self.ignore_filters.default,
            )
        else:
            raise NotImplementedError(
                f"Config does not have support for {type}, even though type is valid"
            )


_ROOT_CONFIG_FIELDS = tuple(f.name for f in fields(DoXtringsConfig))
_IGNORE_FILTERS_FIELDS = tuple(f.name for f in fields(IgnoreFilters))
_IGNORE_FILTERS_BY_TYPE_FIELDS = tuple(f.name for f in fields(IgnoreFiltersRules))


class InvalidConfigFileTypeError(Exception):
    """Exception raised if configuration file is in invalid format"""


_config = None


def set_config(config_file: Optional[str] = None):
    """Sets the global DoXtrings configuration object.

    Args:
        config_file (Optional[str], optional): the file from which to parse the configuration.
            Defaults to None.
    """
    config = _initialize_config(config_file)
    global _config
    _config = config


def load_config() -> DoXtringsConfig:
    """Loads the global configuration

    Raises:
        ValueError: raised if config was not previously set using 'set_config'

    Returns:
        DoXtringsConfig: returns the DoxtringsConfig object.
    """
    if _config is None:
        raise ValueError("Config loaded before it was initialized")
    return _config


def _initialize_config(config_file: Optional[str] = None) -> DoXtringsConfig:
    if config_file:
        if not Path(config_file).is_file():
            raise FileNotFoundError(f"File {config_file} does not exist")
    config_files = (
        [Path(config_file)]
        if config_file is not None
        else [Path(f) for f in _DEFAULT_CONFIG_FILES]
    )
    for file_path in config_files:
        logger.info(f"Looking for config file at {str(file_path)}")
        cfg_dict = _load_cfg_if_exists(file_path)
        if cfg_dict is not None:
            logger.info(f"Read config file {str(file_path)}")
            return _build_config(cfg_dict)
    return DoXtringsConfig()


def _build_config(cfg_dict: Dict[str, Any]) -> DoXtringsConfig:
    _check_fields(cfg_dict, valid_fields=_ROOT_CONFIG_FIELDS)
    ignore_filters_rules_dict = cfg_dict.pop("ignore_filters", {})
    _check_fields(
        ignore_filters_rules_dict,
        valid_fields=_IGNORE_FILTERS_BY_TYPE_FIELDS,
        field_prefix="ignore_filters.",
    )
    ignore_filters_rules_kwargs: Dict[str, IgnoreFilters] = {}
    for field in _IGNORE_FILTERS_BY_TYPE_FIELDS:
        ignore_dict: Dict[str, Any] = ignore_filters_rules_dict.get(field, {})
        _check_fields(
            ignore_dict,
            valid_fields=_IGNORE_FILTERS_FIELDS,
            field_prefix=f"ignore_filters.{field}.",
        )
        ignore_filters_rules_kwargs[field] = IgnoreFilters(**ignore_dict)
    ignore_filters_rules = IgnoreFiltersRules(**ignore_filters_rules_kwargs)

    return DoXtringsConfig(
        **cfg_dict,
        ignore_filters=ignore_filters_rules,
    )


def _check_fields(
    cfg_dict: Dict[str, Any], valid_fields: Tuple[str, ...], field_prefix: str = ""
):
    invalid_fields: List[str] = []
    for key in cfg_dict.keys():
        if key not in valid_fields:
            invalid_fields.append(field_prefix + key)
    if len(invalid_fields) > 0:
        raise TypeError(
            f"Unexpected DoXtringsConfig fields: {', '.join(sorted(invalid_fields))}"
        )


def _load_cfg_if_exists(cfg_path: Path) -> Optional[Dict[str, Any]]:
    if cfg_path.exists() and cfg_path.is_file():
        parsed_dict = _parse_file(cfg_path)
        # If file is pyproject.toml, get only the correct section
        if cfg_path.name == "pyproject.toml":
            logger.info(
                f"Config file is pyproject.toml, will look for specific section"
            )
            toml_dict = _get_pyproject_toml_section(parsed_dict)
            if toml_dict is None:
                logger.info(f"doxtrings config not found in pyproject.toml")
                return None
            else:
                parsed_dict = toml_dict
        return parsed_dict
    else:
        return None


def _parse_file(cfg_path: Path) -> Dict[str, Any]:
    parser_module = _get_parser_module(cfg_path)
    with cfg_path.open("rb") as cfg_file:
        parsed_dict: Dict[str, Any] = parser_module.load(cfg_file)

        return parsed_dict


def _get_parser_module(cfg_file: Path) -> ModuleType:
    if cfg_file.suffix == ".toml":
        return tomli
    elif cfg_file.suffix == ".json":
        return json
    else:
        raise InvalidConfigFileTypeError(
            f"Allowed config types are '.toml' and '.json', but found '{cfg_file.suffix}'"
        )


def _get_pyproject_toml_section(
    parsed_dict: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    try:
        return parsed_dict["tool"]["doxtrings"]
    except:
        return None
