"""Language-specific analysis modules.

Provides auto-discovery and registry for all 201+ language modules.

Usage:
    from toponymia.languages import get_module, get_all_modules, list_modules

    # Get a specific module by ISO 639-3 code
    old_norse = get_module("non")
    results = old_norse.segment("Bjørgvin")

    # Get all modules
    modules = get_all_modules()

    # List available language codes
    codes = list_modules()
"""

from __future__ import annotations

import importlib
import pkgutil

from toponymia.languages.base import BaseLanguageModule, LanguageClassification, SegmentationResult

__all__ = [
    "BaseLanguageModule",
    "EtymologyCandidate",
    "LanguageClassification",
    "SegmentationResult",
    "get_all_modules",
    "get_module",
    "list_modules",
]

from toponymia.languages.base import EtymologyCandidate

# Lazily populated registry: language_code -> module instance
_registry: dict[str, BaseLanguageModule] | None = None


def _build_registry() -> dict[str, BaseLanguageModule]:
    """Scan the languages package and instantiate all modules."""
    registry: dict[str, BaseLanguageModule] = {}
    package_path = __path__
    for _importer, modname, _ispkg in pkgutil.iter_modules(package_path):
        if modname == "base" or modname.startswith("_"):
            continue
        try:
            module = importlib.import_module(f"toponymia.languages.{modname}")
        except ImportError:
            continue
        # Find all BaseLanguageModule subclasses in this module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseLanguageModule)
                and attr is not BaseLanguageModule
                and attr.language_code  # Must have a code defined
            ):
                instance = attr()
                registry[instance.language_code] = instance
    return registry


def _get_registry() -> dict[str, BaseLanguageModule]:
    """Get or build the module registry (lazy singleton)."""
    global _registry  # noqa: PLW0603
    if _registry is None:
        _registry = _build_registry()
    return _registry


def get_module(language_code: str) -> BaseLanguageModule:
    """Get a language module instance by ISO 639-3 code.

    Args:
        language_code: ISO 639-3 language code (e.g., "non" for Old Norse).

    Returns:
        The language module instance.

    Raises:
        KeyError: If no module exists for the given code.
    """
    registry = _get_registry()
    if language_code not in registry:
        available = ", ".join(sorted(registry.keys())[:20])
        msg = f"No language module for code '{language_code}'. Available (first 20): {available}..."
        raise KeyError(msg)
    return registry[language_code]


def get_all_modules() -> dict[str, BaseLanguageModule]:
    """Get all available language modules.

    Returns:
        Dict mapping language codes to module instances.
    """
    return dict(_get_registry())


def list_modules() -> list[str]:
    """List all available language codes.

    Returns:
        Sorted list of ISO 639-3 codes with available modules.
    """
    return sorted(_get_registry().keys())
