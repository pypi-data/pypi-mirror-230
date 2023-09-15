import logging
import re
import string
from typing import Dict, Iterable, Optional, Type, Union

from .exceptions import (
    IncompleteVersionRepresentationException,
    InvalidVersionPartException,
    MissingValueForSerializationException,
    VersionConfigInitializationException,
)
from .functions import NumericFunction, ValuesFunction
from .utils import keyvaluestring


logger = logging.getLogger(__name__)


class PartType:
    BRANCH = "branch"


class PartConfiguration:
    # TODO: Move *Function classes functionality into this class

    function_cls: Union[Type[NumericFunction], Type[ValuesFunction]]

    def __init__(self, *args, **kwds):
        self.function = self.function_cls(*args, **kwds)

    @property
    def first_value(self) -> str:
        return str(self.function.first_value)

    @property
    def optional_value(self) -> str:
        return str(self.function.optional_value)

    @property
    def independent(self) -> bool:
        return self.function.independent

    def bump(self, value: str):
        return self.function.bump(value)

    def null(self, _: str) -> str:
        return self.function.first_value

    def copy(self, value: str) -> str:
        return value


class ConfiguredVersionPartConfiguration(PartConfiguration):
    function_cls = ValuesFunction


class NumericVersionPartConfiguration(PartConfiguration):
    function_cls = NumericFunction


class VCSBranchPartConfiguration:

    part_name = "branch"

    class Parameter:
        BASE_BRANCH = "base_branch"

    def __init__(self, base_branch: str, current_branch: Optional[str] = None) -> None:
        if current_branch is None:
            raise ValueError(f"Error getting current branch name. The {self.part_name} part cannot be used.")
        if not isinstance(base_branch, str):
            raise ValueError(f"The {self.Parameter.BASE_BRANCH} parameter should be string.")
        self.base_branch = base_branch
        self.optional_value = base_branch
        self.current_branch = current_branch
        self.independent = False

    def bump(self, value: str) -> str:
        branch_during_bump = value
        if self.current_branch == self.base_branch:
            raise ValueError(f"Can't bump the {self.part_name} part in the base branch.")
        if branch_during_bump == self.current_branch:
            raise ValueError(f"The {self.part_name} part already has value '{branch_during_bump}'.")
        if branch_during_bump != self.base_branch:
            raise ValueError(
                f"The {self.part_name} part is already set to {self.current_branch} and can't be changed "
                f"to {branch_during_bump}, it can only be reset by bumping an ancestor part from the base branch."
            )
        return self.current_branch

    def copy(self, value: str) -> str:
        branch_from_previous_version = value
        if self.base_branch == self.current_branch == branch_from_previous_version:
            raise ValueError(
                f"Bumping a descendant of the {self.part_name} part isn't allowed in the base branch."
            )
        if branch_from_previous_version in (self.base_branch, self.current_branch):
            return self.current_branch
        raise ValueError(
                f"The {self.part_name} part is already set to {self.current_branch} "
                f"and can't be changed to {branch_from_previous_version}."
            )

    def null(self, *_args, **_kwargs) -> str:
        if self.current_branch != self.base_branch:
            raise ValueError(
                "Bumping an ancestor part is allowed only in the base branch."
            )
        return self.current_branch


class VersionPart:
    """
    Represent part of a version number.

    Offer a self.config object that rules how the part behaves when
    increased or reset.

    TODO: Merge *Function classes with the descendant of this one.
    """

    def __init__(self, value: str, config=None):
        self._value = value

        if config is None:
            config = NumericVersionPartConfiguration()

        self.config: Union[
            NumericVersionPartConfiguration, ConfiguredVersionPartConfiguration, VCSBranchPartConfiguration
        ] = config

    @property
    def value(self) -> str:
        return self._value or self.config.optional_value

    def copy(self) -> "VersionPart":
        return VersionPart(value=self.config.copy(self.value), config=self.config)

    def bump(self) -> "VersionPart":
        return VersionPart(value=self.config.bump(self.value), config=self.config)

    def null(self) -> "VersionPart":
        return VersionPart(value=self.config.null(self.value), config=self.config)

    def is_optional(self) -> bool:
        return self.value == self.config.optional_value

    def is_independent(self) -> bool:
        return self.config.independent

    def __format__(self, format_spec) -> str:
        return self.value

    def __repr__(self):
        return "<bump4version.VersionPart:{}:{}>".format(self.config.__class__.__name__, self.value)

    def __eq__(self, other):
        return self.value == other.value


class Version:
    def __init__(self, values: Dict[str, VersionPart], original=None) -> None:
        self._values: Dict[str, VersionPart] = dict(values)
        self.original = original

    def __getitem__(self, key):
        return self._values[key]

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def items(self):
        return self._values.items()

    def __repr__(self):
        return "<bump4version.Version:{}>".format(keyvaluestring(self._values))

    def bump(self, part_name: str, order: Iterable[str]) -> "Version":
        bumped = False

        new_values = {}

        for label in order:
            if label not in self._values:
                continue
            part = self._values[label]
            if label == part_name:
                new_values[label] = part.bump()
                bumped = True
            elif bumped and not part.is_independent():
                new_values[label] = part.null()
            else:
                new_values[label] = part.copy()

        if not bumped:
            raise InvalidVersionPartException("No part named %r" % part_name)

        new_version = Version(new_values)

        return new_version


def labels_for_format(serialize_format):
    return (label for _, label, _, _ in string.Formatter().parse(serialize_format) if label)


class VersionConfig:
    """
    Hold a complete representation of a version string.
    """

    def __init__(self, parse, serialize, search, replace, part_configs=None):
        try:
            self.parse_regex = re.compile(parse, re.VERBOSE)
        except re.error:
            logger.error("--parse '%s' is not a valid regex", parse)
            raise VersionConfigInitializationException

        self.serialize_formats = serialize

        if not part_configs:
            part_configs = {}

        self.part_configs = part_configs
        self.search = search
        self.replace = replace

    def order(self):
        # currently, order depends on the first given serialization format
        # this seems like a good idea because this should be the most complete format
        return labels_for_format(self.serialize_formats[0])

    def parse(self, version_string: Optional[str]) -> Optional[Version]:
        if not version_string:
            return None

        regexp_one_line = "".join([line.split("#")[0].strip() for line in self.parse_regex.pattern.splitlines()])

        logger.info(
            "Parsing version '%s' using regexp '%s'",
            version_string,
            regexp_one_line,
        )

        match = self.parse_regex.search(version_string)

        _parsed = {}
        if not match:
            logger.warning(
                "Evaluating 'parse' option: '%s' does not parse current version '%s'",
                self.parse_regex.pattern,
                version_string,
            )
            return None

        for key, value in match.groupdict().items():
            _parsed[key] = VersionPart(value, self.part_configs.get(key))

        v = Version(_parsed, version_string)

        logger.info("Parsed the following values: %s", keyvaluestring(v._values))

        return v

    def _serialize(self, version, serialize_format, context, raise_if_incomplete=False):
        """
        Attempts to serialize a version with the given serialization format.

        Raises MissingValueForSerializationException if not serializable
        """
        values = context.copy()
        for part_name, version_part in version.items():
            values[part_name] = version_part

        # TODO dump complete context on debug level

        try:
            # test whether all parts required in the format have values
            serialized = serialize_format.format(**values)

        except KeyError as e:
            missing_key = getattr(e, "message", e.args[0])
            raise MissingValueForSerializationException(
                "Did not find key {} in {} when serializing version number".format(repr(missing_key), repr(version))
            ) from None

        keys_needing_representation = set()

        keys = list(self.order())
        for i, k in enumerate(keys):
            v = values[k]

            if not isinstance(v, VersionPart):
                # values coming from environment variables don't need
                # representation
                continue

            if not v.is_optional():
                keys_needing_representation = set(keys[: i + 1])

        required_by_format = set(labels_for_format(serialize_format))

        # try whether all parsed keys are represented
        if raise_if_incomplete:
            if not keys_needing_representation <= required_by_format:
                raise IncompleteVersionRepresentationException(
                    "Could not represent '{}' in format '{}'".format(
                        "', '".join(keys_needing_representation ^ required_by_format),
                        serialize_format,
                    )
                )

        return serialized

    def _choose_serialize_format(self, version, context):
        chosen = None

        logger.debug("Available serialization formats: '%s'", "', '".join(self.serialize_formats))

        for serialize_format in self.serialize_formats:
            try:
                self._serialize(version, serialize_format, context, raise_if_incomplete=True)
                # Prefer shorter or first search expression.
                chosen_part_count = None if not chosen else len(list(string.Formatter().parse(chosen)))
                serialize_part_count = len(list(string.Formatter().parse(serialize_format)))
                if not chosen or chosen_part_count > serialize_part_count:
                    chosen = serialize_format
                    logger.debug("Found '%s' to be a usable serialization format", chosen)
                else:
                    logger.debug("Found '%s' usable serialization format, but it's longer", serialize_format)
            except IncompleteVersionRepresentationException:
                # If chosen, prefer shorter
                if not chosen:
                    chosen = serialize_format
            except MissingValueForSerializationException as e:
                logger.info(e.message)
                raise e

        if not chosen:
            raise KeyError("Did not find suitable serialization format")

        logger.debug("Selected serialization format '%s'", chosen)

        return chosen

    def serialize(self, version, context):
        serialized = self._serialize(version, self._choose_serialize_format(version, context), context)
        logger.debug("Serialized to '%s'", serialized)
        return serialized
