import typing
from types import ModuleType, FunctionType
from typing import Protocol, NewType, Any, TypeGuard, Type, Callable

PatchTarget = NewType("PatchTarget", str)


class Named(Protocol):
    __name__: str


class InvalidPatchTargetException(Exception):
    pass


def is_named(value: Any) -> TypeGuard[Named]:
    return hasattr(value, "__name__")


def patch_target(
        host_module: ModuleType, object_to_be_patched: ModuleType | Callable[[Any], Any] | Type[Any] | str
) -> PatchTarget:
    match object_to_be_patched:
        case v if is_named(v):
            name = v.__name__
        case _:
            name = v

    if not hasattr(host_module, name):
        raise InvalidPatchTargetException(f"{name} not found within {host_module.__name__}")

    return PatchTarget(f"{host_module.__name__}.{name}")


__all__ = ["patch_target"]