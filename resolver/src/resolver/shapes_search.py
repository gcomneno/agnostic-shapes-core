"""Bounded structural search over the intrinsic SHAPES edit graph.

This module is a Resolver satellite over SHAPES. It does not extend SHAPES
semantics and does not depend on the legacy ``petra`` runtime.

The graph is induced solely by intrinsic ``ADD`` and ``REMOVE`` edits.
Search policy, derived metrics, bounds, and path result types remain Resolver
concerns rather than SHAPES core contracts.
"""

from __future__ import annotations

import heapq
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import Enum
from itertools import count

from shapes import (
    OccurrencePath,
    Shape,
    add,
    height,
    iter_occurrences,
    leaf_count,
    remove,
    size,
    validate,
)


class ShapesSearchError(ValueError):
    """A deterministic SHAPES search failure."""


class EditDirection(str, Enum):
    """Intrinsic edit direction recorded by a Resolver path."""

    ADD = "ADD"
    REMOVE = "REMOVE"


@dataclass(frozen=True)
class ShapeStep:
    """One intrinsic structural edit along a resolved path."""

    direction: EditDirection
    target: OccurrencePath
    before_shape: Shape
    after_shape: Shape


@dataclass(frozen=True)
class ShapePath:
    """A bounded shortest path between two SHAPES values."""

    source: Shape
    target: Shape
    steps: tuple[ShapeStep, ...]
    explored: int = 0

    @property
    def length(self) -> int:
        return len(self.steps)


def _neighbors(shape: Shape) -> Iterator[ShapeStep]:
    """Yield every distinct one-step intrinsic successor.

    Equal target occurrences may induce structurally equal successors.
    Successors are therefore deduplicated by ``Shape`` equality rather than
    by occurrence path.
    """

    seen: set[Shape] = {shape}

    for path, _occurrence in iter_occurrences(shape):
        after = add(shape, path)
        if after in seen:
            continue
        seen.add(after)
        yield ShapeStep(
            direction=EditDirection.ADD,
            target=path,
            before_shape=shape,
            after_shape=after,
        )

    for path, occurrence in iter_occurrences(shape):
        if not path or occurrence.children:
            continue

        after = remove(shape, path)
        if after in seen:
            continue
        seen.add(after)
        yield ShapeStep(
            direction=EditDirection.REMOVE,
            target=path,
            before_shape=shape,
            after_shape=after,
        )


def _build_cached_metrics(
    target: Shape,
) -> tuple[
    Callable[[Shape], int],
    Callable[[Shape], int],
]:
    """Return cached ``(heuristic, shape_size)`` functions."""

    size_cache: dict[Shape, int] = {}
    depth_cache: dict[Shape, int] = {}
    leaf_cache: dict[Shape, int] = {}
    heuristic_cache: dict[Shape, int] = {}

    target_size = size(target)
    target_depth = height(target)
    target_leaves = leaf_count(target)

    def shape_size(shape: Shape) -> int:
        cached = size_cache.get(shape)
        if cached is None:
            cached = size(shape)
            size_cache[shape] = cached
        return cached

    def cached_height(shape: Shape) -> int:
        cached = depth_cache.get(shape)
        if cached is None:
            cached = height(shape)
            depth_cache[shape] = cached
        return cached

    def cached_leaf_count(shape: Shape) -> int:
        cached = leaf_cache.get(shape)
        if cached is None:
            cached = leaf_count(shape)
            leaf_cache[shape] = cached
        return cached

    def heuristic(shape: Shape) -> int:
        cached = heuristic_cache.get(shape)
        if cached is None:
            cached = max(
                abs(shape_size(shape) - target_size),
                abs(cached_height(shape) - target_depth),
                abs(cached_leaf_count(shape) - target_leaves),
            )
            heuristic_cache[shape] = cached
        return cached

    return heuristic, shape_size


def resolve_shapes(
    source: Shape,
    target: Shape,
    *,
    max_depth: int = 10,
    max_nodes: int = 20,
    max_visited: int = 1000,
) -> ShapePath:
    """Find a shortest bounded path in the intrinsic SHAPES edit graph.

    ``max_nodes`` is a SHAPES structural bound and therefore means
    ``size(shape) <= max_nodes``. It is not the legacy PETRA ``node_count``
    compatibility metric.
    """

    if max_depth < 0:
        raise ShapesSearchError("max_depth must be >= 0")
    if max_nodes < 1:
        raise ShapesSearchError("max_nodes must be >= 1")
    if max_visited < 1:
        raise ShapesSearchError("max_visited must be >= 1")

    validate(source)
    validate(target)

    heuristic, shape_size = _build_cached_metrics(target)

    if shape_size(source) > max_nodes:
        raise ShapesSearchError("source shape exceeds max_nodes")
    if shape_size(target) > max_nodes:
        raise ShapesSearchError("target shape exceeds max_nodes")

    if source == target:
        return ShapePath(source=source, target=target, steps=(), explored=0)

    tie = count()
    open_set: list[
        tuple[int, int, int, Shape, tuple[ShapeStep, ...]]
    ] = [
        (heuristic(source), 0, next(tie), source, ())
    ]
    best_g: dict[Shape, int] = {source: 0}
    explored = 0

    while open_set:
        _f, g, _, current, current_path = heapq.heappop(open_set)

        known_g = best_g.get(current)
        if known_g is not None and known_g < g:
            continue

        # Goal must be checked before depth pruning so a target reached
        # exactly at max_depth remains admissible.
        if current == target:
            return ShapePath(
                source=source,
                target=target,
                steps=current_path,
                explored=explored,
            )

        if g >= max_depth:
            continue

        explored += 1
        if explored > max_visited:
            raise ShapesSearchError(
                "explored more than "
                f"{max_visited} shapes without finding a path"
            )

        for step in _neighbors(current):
            neighbor = step.after_shape

            if shape_size(neighbor) > max_nodes:
                continue

            new_g = g + 1
            previous_g = best_g.get(neighbor)
            if previous_g is not None and new_g >= previous_g:
                continue

            best_g[neighbor] = new_g
            new_path = (*current_path, step)

            heapq.heappush(
                open_set,
                (
                    new_g + heuristic(neighbor),
                    new_g,
                    next(tie),
                    neighbor,
                    new_path,
                ),
            )

    raise ShapesSearchError(
        f"no path found within max_depth={max_depth}, "
        f"max_nodes={max_nodes}"
    )
