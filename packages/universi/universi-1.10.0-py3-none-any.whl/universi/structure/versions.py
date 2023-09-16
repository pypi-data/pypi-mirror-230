from dataclasses import dataclass
import datetime
import functools
from collections import defaultdict
from collections.abc import Callable, Sequence
from contextvars import ContextVar
from enum import Enum
from typing import Any, ClassVar, ParamSpec, TypeAlias, TypeVar

from fastapi.routing import _prepare_response_content
from typing_extensions import assert_never

from universi.exceptions import UniversiError, UniversiStructureError
from universi.structure.endpoints import AlterEndpointSubInstruction, EndpointWasInstruction
from universi.structure.enums import AlterEnumSubInstruction

from .._utils import Sentinel
from .common import Endpoint, VersionedModel, VersionDate
from .data import AlterRequestBodyInstruction, AlterResponseInstruction
from .schemas import AlterSchemaInstruction, AlterSchemaSubInstruction, SchemaPropertyDefinitionInstruction
from pydantic.fields import ModelField
from universi._utils import get_another_version_of_cls

_P = ParamSpec("_P")
_R = TypeVar("_R")
PossibleInstructions: TypeAlias = (
    AlterSchemaSubInstruction | AlterEndpointSubInstruction | AlterEnumSubInstruction | AlterSchemaInstruction
)


class VersionChange:
    description: ClassVar[str] = Sentinel
    instructions_to_migrate_to_previous_version: ClassVar[Sequence[PossibleInstructions]] = Sentinel
    alter_schema_instructions: ClassVar[Sequence[AlterSchemaSubInstruction | AlterSchemaInstruction]] = Sentinel
    alter_enum_instructions: ClassVar[Sequence[AlterEnumSubInstruction]] = Sentinel
    alter_endpoint_instructions: ClassVar[Sequence[AlterEndpointSubInstruction | EndpointWasInstruction]] = Sentinel
    alter_response_instructions: ClassVar[dict[Any, AlterResponseInstruction]] = Sentinel
    alter_request_body_instructions: ClassVar[dict[Any, AlterRequestBodyInstruction]] = Sentinel
    _bound_versions: "VersionBundle | None"

    def __init_subclass__(cls, _abstract: bool = False) -> None:
        if _abstract:
            return
        cls._validate_subclass()

        cls.alter_schema_instructions = []
        cls.alter_enum_instructions = []
        cls.alter_endpoint_instructions = []
        cls.alter_response_instructions = {}
        cls.alter_request_body_instructions = {}
        for alter_instruction in cls.instructions_to_migrate_to_previous_version:
            if isinstance(alter_instruction, AlterSchemaSubInstruction | AlterSchemaInstruction):
                cls.alter_schema_instructions.append(alter_instruction)
            elif isinstance(alter_instruction, AlterEnumSubInstruction):
                cls.alter_enum_instructions.append(alter_instruction)
            elif isinstance(alter_instruction, AlterEndpointSubInstruction):
                cls.alter_endpoint_instructions.append(alter_instruction)
            else:
                assert_never(alter_instruction)
        for instruction in cls.__dict__.values():
            if isinstance(instruction, SchemaPropertyDefinitionInstruction):
                cls.alter_schema_instructions.append(instruction)
            elif isinstance(instruction, AlterResponseInstruction):
                cls.alter_response_instructions[instruction.schema] = instruction
            elif isinstance(instruction, EndpointWasInstruction):
                cls.alter_endpoint_instructions.append(instruction)
            elif isinstance(instruction, AlterRequestBodyInstruction):
                cls.alter_request_body_instructions[instruction.schema] = instruction

        cls._check_no_subclassing()
        cls._bound_versions = None

    @classmethod
    def _validate_subclass(cls):
        if cls.description is Sentinel:
            raise UniversiStructureError(
                f"Version change description is not set on '{cls.__name__}' but is required.",
            )
        if cls.instructions_to_migrate_to_previous_version is Sentinel:
            raise UniversiStructureError(
                f"Attribute 'instructions_to_migrate_to_previous_version' is not set on '{cls.__name__}'"
                " but is required.",
            )
        if not isinstance(cls.instructions_to_migrate_to_previous_version, Sequence):
            raise UniversiStructureError(
                f"Attribute 'instructions_to_migrate_to_previous_version' must be a sequence in '{cls.__name__}'.",
            )
        for instruction in cls.instructions_to_migrate_to_previous_version:
            if not isinstance(instruction, PossibleInstructions):
                raise UniversiStructureError(
                    f"Instruction '{instruction}' is not allowed. Please, use the correct instruction types",
                )
        for attr_name, attr_value in cls.__dict__.items():
            if not isinstance(
                attr_value,
                AlterResponseInstruction
                | SchemaPropertyDefinitionInstruction
                | EndpointWasInstruction
                | AlterRequestBodyInstruction,
            ) and attr_name not in {
                "description",
                "side_effects",
                "instructions_to_migrate_to_previous_version",
                "__module__",
                "__doc__",
            }:
                raise UniversiStructureError(
                    f"Found: '{attr_name}' attribute of type '{type(attr_value)}' in '{cls.__name__}'."
                    " Only migration instructions and schema properties are allowed in version change class body.",
                )

    @classmethod
    def _check_no_subclassing(cls):
        if cls.mro() != [cls, VersionChange, object]:
            raise TypeError(
                f"Can't subclass {cls.__name__} as it was never meant to be subclassed.",
            )

    def __init__(self) -> None:
        raise TypeError(
            f"Can't instantiate {self.__class__.__name__} as it was never meant to be instantiated.",
        )


class VersionChangeWithSideEffects(VersionChange, _abstract=True):
    @classmethod
    def _check_no_subclassing(cls):
        if cls.mro() != [cls, VersionChangeWithSideEffects, VersionChange, object]:
            raise TypeError(
                f"Can't subclass {cls.__name__} as it was never meant to be subclassed.",
            )

    @classmethod
    @property
    def is_applied(cls) -> bool:
        if cls._bound_versions is None or cls not in cls._bound_versions._version_changes_to_version_mapping:
            raise UniversiError(
                f"You tried to check whether '{cls.__name__}' is active but it was never bound to any version.",
            )
        api_version = cls._bound_versions.api_version_var.get()
        if api_version is None:
            return True
        return cls._bound_versions._version_changes_to_version_mapping[cls] <= api_version


class Version:
    def __init__(self, value: VersionDate, *version_changes: type[VersionChange]) -> None:
        self.value = value
        self.version_changes = version_changes

    def __repr__(self) -> str:
        return f"Version('{self.value}')"


class VersionBundle:
    def __init__(
        self,
        *versions: Version,
        api_version_var: ContextVar[VersionDate | None],
    ) -> None:
        self.versions = versions
        self.api_version_var = api_version_var
        if sorted(versions, key=lambda v: v.value, reverse=True) != list(versions):
            raise ValueError(
                "Versions are not sorted correctly. Please sort them in descending order.",
            )
        for version in versions:
            for version_change in version.version_changes:
                if version_change._bound_versions is not None:
                    raise UniversiStructureError(
                        f"You tried to bind version change '{version_change.__name__}' to two different versions. "
                        "It is prohibited.",
                    )
                version_change._bound_versions = self

    def __iter__(self):
        yield from self.versions

    @functools.cached_property
    def versioned_schemas(self) -> dict[str, type[VersionedModel]]:
        return {
            f"{instruction.schema.__module__}.{instruction.schema.__name__}": instruction.schema
            for version in self.versions
            for version_change in version.version_changes
            for instruction in version_change.alter_schema_instructions
        }

    @functools.cached_property
    def versioned_enums(self) -> dict[str, type[Enum]]:
        return {
            f"{instruction.enum.__module__}.{instruction.enum.__name__}": instruction.enum
            for version in self.versions
            for version_change in version.version_changes
            for instruction in version_change.alter_enum_instructions
        }

    @functools.cached_property
    def _version_changes_to_version_mapping(
        self,
    ) -> dict[type[VersionChange], VersionDate]:
        return {
            version_change: version.value for version in self.versions for version_change in version.version_changes
        }

    def migrate_response(
        self,
        response_model: Any,
        data: Any,
        current_version: VersionDate,
    ) -> dict[str, Any]:
        """Convert the data to a specific version by applying all version changes in reverse order.

        Args:
            endpoint: the function which usually returns this data. Data migrations marked with this endpoint will
            be applied to the passed data
            data: data to be migrated. Will be mutated during the call
            version: the version to which the data should be converted

        Returns:
            Modified data
        """

        for v in self.versions:
            if v.value <= current_version:
                break
            for version_change in v.version_changes:
                if response_model in version_change.alter_response_instructions:
                    version_change.alter_response_instructions[response_model](data)
        return data

    # TODO: Add an assertion that there is only one such instruction per version per schema
    def migrate_request(self, *, body_type: type, body: Any, current_version: VersionDate):
        for v in reversed(self.versions):
            # 2000
            # 2001 -
            # 2002
            # 2003
            if v.value <= current_version:
                continue
            for version_change in v.version_changes:
                if body_type in version_change.alter_request_body_instructions:
                    body = version_change.alter_request_body_instructions[body_type](body)
        return body

    def versioned(
        self,
        response_model: Any,
        *,
        body_params: Sequence[ModelField] = (),
    ) -> Callable[[Endpoint[_P, _R]], Endpoint[_P, _R]]:
        def wrapper(endpoint: Endpoint[_P, _R]) -> Endpoint[_P, _R]:
            @functools.wraps(endpoint)
            async def decorator(*args: _P.args, **kwargs: _P.kwargs) -> _R:
                self._convert_endpoint_args_to_version(decorator.body_params, args, kwargs)
                return await self._convert_endpoint_response_to_version(
                    decorator.func,  # pyright: ignore[reportGeneralTypeIssues]
                    decorator.response_model,
                    args,
                    kwargs,
                )

            # This is useful to go around FastAPI's hardcoded "iscoroutinefunction" checks and to keep the info about the
            # original schema that was used to generate the endpoint.
            decorator.func = endpoint  # pyright: ignore[reportGeneralTypeIssues]
            decorator.response_model = response_model  # pyright: ignore[reportGeneralTypeIssues]
            decorator.body_params = body_params  # pyright: ignore[reportGeneralTypeIssues]
            return decorator

        return wrapper

    async def _convert_endpoint_response_to_version(
        self,
        func_to_get_response_from: Endpoint,
        response_model: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:
        response = await func_to_get_response_from(*args, **kwargs)
        api_version = self.api_version_var.get()
        if api_version is None:
            return response
        # TODO We probably need to call this in the same way as in fastapi instead of hardcoding exclude_unset.
        # We have such an ability if we force passing the route into this wrapper. Or maybe not... Important!
        response = _prepare_response_content(response, exclude_unset=False)
        return self.migrate_response(response_model, response, api_version)

    def _convert_endpoint_args_to_version(
        self, body_params: Sequence[ModelField], args: tuple[Any, ...], kwargs: dict[str, Any]
    ):
        api_version = self.api_version_var.get()
        if api_version is None:
            return args, kwargs
        if len(body_params) == 1:
            body_param = body_params[0]
            body = kwargs[body_param.alias]
            kwargs[body_param.alias] = self.migrate_request(
                body_type=body_param.type_, body=body, current_version=api_version
            )
        return args, kwargs


@dataclass(slots=True)
class ResponseMigrator:
    response_model: Any
    endpoint: Endpoint
    versions: VersionBundle

    def __post_init__(self):
        functools.update_wrapper(self, self.endpoint)

    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass
