"""A minimal subset of Pydantic for local testing without external dependencies."""

from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Any, ClassVar, Dict, Optional, Tuple, Union, get_args, get_origin, get_type_hints, Annotated

_MISSING = object()


@dataclass
class FieldInfo:
    default: Any = _MISSING
    default_factory: Any = _MISSING
    metadata: Tuple[Any, ...] = ()
    annotation: Any = None


def Field(*, default: Any = _MISSING, default_factory: Any = _MISSING) -> FieldInfo:
    return FieldInfo(default=default, default_factory=default_factory)


class ConfigDict(dict):
    """Simple stand-in for :class:`pydantic.ConfigDict`."""


class BaseModel:
    model_fields: ClassVar[Dict[str, FieldInfo]] = {}
    model_config: ClassVar[ConfigDict] = ConfigDict()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._build_model_fields()

    @classmethod
    def _build_model_fields(cls) -> None:
        module = sys.modules.get(cls.__module__)
        globalns = dict(getattr(module, "__dict__", {}))
        globalns.setdefault("Dict", Dict)
        globalns.setdefault("ClassVar", ClassVar)
        globalns.setdefault("Union", Union)
        globalns.setdefault("Optional", Optional)
        globalns.setdefault("FieldInfo", FieldInfo)
        globalns.setdefault("ConfigDict", ConfigDict)
        localns = dict(globalns)
        localns.update(cls.__dict__)
        try:
            hints = get_type_hints(cls, globalns=globalns, localns=localns, include_extras=True)
        except NameError:
            hints = {}
            annotations = getattr(cls, "__annotations__", {})
            for name, annotation in annotations.items():
                if name.startswith("__"):
                    continue
                hints[name] = annotation
        model_fields: Dict[str, FieldInfo] = {}
        for name, annotation in hints.items():
            if get_origin(annotation) is ClassVar:
                continue
            default_value = getattr(cls, name, _MISSING)
            if isinstance(default_value, FieldInfo):
                field_info = default_value
            else:
                field_info = FieldInfo(default=default_value)
            field_info.annotation = annotation
            field_info.metadata = tuple(field_info.metadata) + _annotation_metadata(annotation)
            model_fields[name] = field_info
            setattr(cls, name, None)
        cls.model_fields = model_fields

    def __init__(self, **data: Any) -> None:
        for name, field in self.model_fields.items():
            if name in data:
                value = data[name]
            else:
                if field.default_factory is not _MISSING:
                    value = field.default_factory()
                elif field.default is not _MISSING:
                    value = field.default
                else:
                    value = None
            setattr(self, name, value)

    def model_dump(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for name in self.model_fields:
            result[name] = _dump_value(getattr(self, name))
        return result

    @classmethod
    def model_rebuild(cls) -> None:
        cls._build_model_fields()


def _dump_value(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [_dump_value(item) for item in value]
    return value


def _annotation_metadata(annotation: Any) -> Tuple[Any, ...]:
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        return tuple(args[1:])
    return ()


__all__ = ["BaseModel", "ConfigDict", "Field", "FieldInfo"]

