"""Tests for SHAPES-native structural distance and caching."""

from __future__ import annotations

import pytest
from shapes import Shape, add

from resolver.shapes_distance import (
    DistanceCache,
    DistanceError,
    structural_distance_shapes,
)


def _unary(depth: int) -> Shape:
    shape = Shape()
    for _ in range(depth):
        shape = Shape(children=(shape,))
    return shape


def test_distance_identity_is_zero() -> None:
    shape = Shape(children=(Shape(), Shape()))

    assert structural_distance_shapes(shape, shape) == 0


def test_distance_one_add_is_one() -> None:
    source = Shape()
    target = add(source, ())

    assert structural_distance_shapes(source, target) == 1


def test_distance_one_remove_is_one() -> None:
    source = Shape(children=(Shape(),))
    target = Shape()

    assert structural_distance_shapes(source, target) == 1


def test_distance_nested_two_edits() -> None:
    assert structural_distance_shapes(Shape(), _unary(2)) == 2


def test_distance_is_symmetric() -> None:
    a = Shape(children=(Shape(), Shape()))
    b = add(a, (0,))

    assert structural_distance_shapes(a, b) == structural_distance_shapes(b, a)


def test_distance_identity_still_respects_max_nodes() -> None:
    shape = Shape(children=(Shape(),))

    with pytest.raises(DistanceError, match="source shape exceeds max_nodes"):
        structural_distance_shapes(shape, shape, max_nodes=1)


def test_distance_translates_search_failure() -> None:
    with pytest.raises(DistanceError, match="no path found"):
        structural_distance_shapes(
            Shape(),
            _unary(2),
            max_depth=1,
        )


def test_shape_validation_errors_are_not_translated() -> None:
    with pytest.raises(TypeError, match="expected Shape"):
        structural_distance_shapes(
            Shape(),
            object(),  # type: ignore[arg-type]
        )


def test_cache_first_lookup_is_miss_and_repeat_is_hit() -> None:
    cache = DistanceCache()
    a = Shape()
    b = Shape(children=(Shape(),))

    assert cache.distance(a, b) == 1
    assert cache.hits == 0
    assert cache.misses == 1
    assert cache.size == 1

    assert cache.distance(a, b) == 1
    assert cache.hits == 1
    assert cache.misses == 1
    assert cache.size == 1


def test_cache_reversed_pair_reuses_entry() -> None:
    cache = DistanceCache()
    a = Shape()
    b = Shape(children=(Shape(),))

    assert cache.distance(a, b) == 1
    assert cache.distance(b, a) == 1

    assert cache.hits == 1
    assert cache.misses == 1
    assert cache.size == 1


def test_cache_reversed_pair_survives_hash_collision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Shape, "__hash__", lambda self: 0)

    cache = DistanceCache()
    a = Shape()
    b = Shape(children=(Shape(),))

    assert a != b
    assert hash(a) == hash(b)

    assert cache.distance(a, b) == 1
    assert cache.distance(b, a) == 1

    assert cache.hits == 1
    assert cache.misses == 1
    assert cache.size == 1


def test_cache_identity_uses_normal_accounting() -> None:
    cache = DistanceCache()
    shape = Shape(children=(Shape(),))

    assert cache.distance(shape, shape) == 0
    assert cache.hits == 0
    assert cache.misses == 1
    assert cache.size == 1

    assert cache.distance(shape, shape) == 0
    assert cache.hits == 1
    assert cache.misses == 1
    assert cache.size == 1


def test_cache_identity_respects_bounds() -> None:
    cache = DistanceCache(max_nodes=1)
    shape = Shape(children=(Shape(),))

    with pytest.raises(DistanceError, match="source shape exceeds max_nodes"):
        cache.distance(shape, shape)

    assert cache.hits == 0
    assert cache.misses == 1
    assert cache.size == 0


def test_failed_search_counts_miss_but_is_not_cached() -> None:
    cache = DistanceCache(max_depth=1)
    source = Shape()
    target = _unary(2)

    for expected_misses in (1, 2):
        with pytest.raises(DistanceError, match="no path found"):
            cache.distance(source, target)

        assert cache.hits == 0
        assert cache.misses == expected_misses
        assert cache.size == 0
