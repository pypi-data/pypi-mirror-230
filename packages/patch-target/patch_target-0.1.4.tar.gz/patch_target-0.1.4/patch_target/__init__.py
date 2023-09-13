import typing
from types import ModuleType
from typing import Protocol, NewType, Any, TypeGuard, Callable

PatchTarget = NewType("PatchTarget", str)
NamedCallable: typing.TypeAlias = Callable[[Any], Any]


class Named(Protocol):
    __name__: str


class InvalidPatchTargetException(Exception):
    pass


def is_named(value: Named | NamedCallable | str) -> TypeGuard[Named]:
    return hasattr(value, "__name__")


def patch_target(
    host_module: ModuleType, object_to_be_patched: Named | NamedCallable | str
) -> PatchTarget:
    match object_to_be_patched:
        case v if is_named(v):
            name = v.__name__
        case str(v):
            name = v
        case _:
            raise TypeError

    if not hasattr(host_module, name):
        raise InvalidPatchTargetException(
            f"'{name}' not found within {host_module.__name__}"
        )

    return PatchTarget(f"{host_module.__name__}.{name}")


__all__ = ["patch_target"]
