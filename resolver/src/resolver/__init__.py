"""Resolver satellite package.

The maintained Phase 2 structural APIs live in the explicit SHAPES-native
submodules:

- resolver.shapes_search
- resolver.shapes_distance
- resolver.shapes_verify

The package root intentionally exports no compatibility API. Legacy
PETRA-coupled modules remain temporarily present only during migration.
"""

__all__: list[str] = []
