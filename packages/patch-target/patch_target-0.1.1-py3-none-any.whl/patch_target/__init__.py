from types import ModuleType, FunctionType
from typing import Protocol, NewType, Any, TypeGuard, Type, Callable

PatchTarget = NewType("PatchTarget", str)


class Named(Protocol):
    __name__: str


def is_named(value: Any) -> TypeGuard[Named]:
    return hasattr(value, "__name__")


class InvalidPatchTargetException(Exception):
    pass


def patch_target(
        host_module: ModuleType, object_to_be_patched: ModuleType | Callable[[Any], Any] | Type[Any]
) -> PatchTarget:
    if not is_named(object_to_be_patched):
        raise InvalidPatchTargetException(
            f"{object_to_be_patched} must be a module, function, class, or instance of a class."
        )
    if not hasattr(host_module, object_to_be_patched.__name__):
        raise InvalidPatchTargetException(f"{object_to_be_patched.__name__} not found within {host_module.__name__}")

    return PatchTarget(f"{host_module.__name__}.{object_to_be_patched.__name__}")


__all__ = ["patch_target"]