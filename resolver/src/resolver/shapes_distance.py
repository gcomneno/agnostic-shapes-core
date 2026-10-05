"""Structural distance over the intrinsic SHAPES edit graph.

This module is a Resolver satellite over SHAPES. It delegates shortest-path
search to the SHAPES-native Resolver and introduces no numeric, prime,
factorization, parsing, or serialization semantics.
"""

from __future__ import annotations

from shapes import Shape

from .shapes_search import ShapesSearchError, resolve_shapes


class DistanceError(ValueError):
    """A deterministic SHAPES structural-distance failure."""


def structural_distance_shapes(
    a: Shape,
    b: Shape,
    *,
    max_depth: int = 30,
    max_nodes: int = 200,
    max_visited: int = 500_000,
) -> int:
    """Return the minimum intrinsic ADD/REMOVE edit distance.

    Search bounds have exactly the semantics defined by ``resolve_shapes``.
    In particular, identity does not bypass validation or ``max_nodes``.
    """

    try:
        path = resolve_shapes(
            a,
            b,
            max_depth=max_depth,
            max_nodes=max_nodes,
            max_visited=max_visited,
        )
    except ShapesSearchError as error:
        raise DistanceError(str(error)) from error

    return path.length


class DistanceCache:
    """Memoized symmetric SHAPES structural distance.

    Cache keys are unordered pairs of immutable ``Shape`` values. Only
    successful computations are cached. A lookup with no cached value counts
    as a miss even when the subsequent distance computation fails.
    """

    def __init__(
        self,
        *,
        max_depth: int = 30,
        max_nodes: int = 200,
        max_visited: int = 500_000,
    ) -> None:
        self._cache: dict[frozenset[Shape], int] = {}
        self._max_depth = max_depth
        self._max_nodes = max_nodes
        self._max_visited = max_visited
        self.hits = 0
        self.misses = 0

    def distance(self, a: Shape, b: Shape) -> int:
        key = frozenset((a, b))

        cached = self._cache.get(key)
        if cached is not None:
            self.hits += 1
            return cached

        self.misses += 1
        result = structural_distance_shapes(
            a,
            b,
            max_depth=self._max_depth,
            max_nodes=self._max_nodes,
            max_visited=self._max_visited,
        )
        self._cache[key] = result
        return result

    @property
    def size(self) -> int:
        return len(self._cache)
