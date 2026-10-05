"""Import-isolation tests for the SHAPES-native Resolver path."""

from __future__ import annotations

import subprocess
import sys


def test_resolver_root_has_no_legacy_public_api() -> None:
    import resolver

    assert resolver.__all__ == []

    legacy_names = (
        "resolve",
        "ResolverError",
        "DistanceCache",
        "structural_distance_shapes",
        "verify_path",
        "PrimeKey",
        "project",
        "contains",
        "meet",
        "join",
    )

    for name in legacy_names:
        assert not hasattr(resolver, name)


def test_shapes_native_submodules_import_without_petra() -> None:
    program = r"""
import importlib.abc
import sys


class BlockPetra(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "petra" or fullname.startswith("petra."):
            raise ImportError("petra import blocked by isolation regression")
        return None


sys.meta_path.insert(0, BlockPetra())

import resolver
import resolver.shapes_search
import resolver.shapes_distance
import resolver.shapes_verify

assert resolver.__all__ == []
"""

    completed = subprocess.run(
        [sys.executable, "-c", program],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, (
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )
