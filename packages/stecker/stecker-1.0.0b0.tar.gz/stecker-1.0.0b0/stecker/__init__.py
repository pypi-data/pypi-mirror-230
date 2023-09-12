# SPDX-FileCopyrightText: 2023 Jonathan Weth <dev@jonathanweth.de>
#
# SPDX-License-Identifier: Apache-2.0

from importlib import import_module, metadata
from typing import ClassVar, Optional

class RegistryObject:
    _registry: ClassVar[Optional[dict[str, type["RegistryObject"]]]] = None
    _entrypoint: ClassVar[Optional[str]] = None
    name: ClassVar[str] = ""

    def __init_subclass__(cls):
        if getattr(cls, "_registry", None) is None:
            cls._registry = {}

            if cls._entrypoint is not None:
                for ep in metadata.entry_points(group=cls._entrypoint):
                    import_module(ep.module)
        else:
            if not cls.name:
                cls.name = cls.__name__
            cls._register()

    @classmethod
    def _register(cls: type["RegistryObject"]):
        if cls.name and cls.name not in cls._registry:
            cls._registry[cls.name] = cls

    @classmethod
    def registered_objects_dict(cls) -> dict[str, type["RegistryObject"]]:
        """Get dict of registered objects."""
        return cls._registry

    @classmethod
    def registered_objects_list(cls) -> list[type["RegistryObject"]]:
        """Get list of registered objects."""
        return list(cls._registry.values())

    @classmethod
    def get_object_by_name(cls, name: str) -> Optional[type["RegistryObject"]]:
        """Get registered object by name."""
        return cls.registered_objects_dict.get(name)

