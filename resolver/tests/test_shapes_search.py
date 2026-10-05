from __future__ import annotations

import pytest
from shapes import Shape, add, size

from resolver.shapes_search import (
    EditDirection,
    ShapesSearchError,
    _neighbors,
    resolve_shapes,
)


def _unary(depth: int) -> Shape:
    shape = Shape()
    for _ in range(depth):
        shape = Shape(children=(shape,))
    return shape


def test_identity_path_is_empty() -> None:
    shape = Shape(children=(Shape(), Shape()))

    path = resolve_shapes(shape, shape)

    assert path.source == shape
    assert path.target == shape
    assert path.steps == ()
    assert path.length == 0
    assert path.explored == 0


def test_one_add_at_root() -> None:
    source = Shape()
    target = add(source, ())

    path = resolve_shapes(source, target)

    assert path.length == 1
    assert path.steps[0].direction is EditDirection.ADD
    assert path.steps[0].target == ()
    assert path.steps[0].before_shape == source
    assert path.steps[0].after_shape == target


def test_one_remove_of_zero_child_child() -> None:
    source = Shape(children=(Shape(),))
    target = Shape()

    path = resolve_shapes(source, target)

    assert path.length == 1
    assert path.steps[0].direction is EditDirection.REMOVE
    assert path.steps[0].target == (0,)
    assert path.steps[0].after_shape == target


def test_nested_add() -> None:
    source = Shape(children=(Shape(),))
    target = add(source, (0,))

    path = resolve_shapes(source, target)

    assert path.length == 1
    assert path.steps[0].direction is EditDirection.ADD
    assert path.steps[0].target == (0,)


def test_nested_remove() -> None:
    target = Shape(children=(Shape(),))
    source = add(target, (0,))

    path = resolve_shapes(source, target)

    assert path.length == 1
    assert path.steps[0].direction is EditDirection.REMOVE
    assert path.steps[0].target == (0, 0)


def test_equal_sibling_targets_deduplicate_successors() -> None:
    source = Shape(children=(Shape(), Shape()))

    neighbors = list(_neighbors(source))

    assert len(neighbors) == 3
    assert len({step.after_shape for step in neighbors}) == 3
    assert {size(step.after_shape) for step in neighbors} == {2, 4}


def test_shortest_path_uses_intrinsic_size_difference() -> None:
    source = Shape()
    target = _unary(2)

    path = resolve_shapes(source, target)

    assert path.length == 2
    assert [step.direction for step in path.steps] == [
        EditDirection.ADD,
        EditDirection.ADD,
    ]


def test_target_at_exact_max_depth_is_accepted() -> None:
    source = Shape()
    target = _unary(2)

    path = resolve_shapes(source, target, max_depth=2)

    assert path.length == 2


def test_target_beyond_max_depth_is_rejected() -> None:
    source = Shape()
    target = _unary(2)

    with pytest.raises(ShapesSearchError, match="no path found"):
        resolve_shapes(source, target, max_depth=1)


def test_max_nodes_uses_shapes_size() -> None:
    source = Shape()
    target = Shape(children=(Shape(),))

    assert size(target) == 2

    with pytest.raises(
        ShapesSearchError,
        match="target shape exceeds max_nodes",
    ):
        resolve_shapes(source, target, max_nodes=1)


def test_identity_path_still_enforces_max_nodes() -> None:
    shape = Shape(children=(Shape(),))

    assert size(shape) == 2

    with pytest.raises(
        ShapesSearchError,
        match="source shape exceeds max_nodes",
    ):
        resolve_shapes(shape, shape, max_nodes=1)


def test_max_visited_bounds_expansion() -> None:
    source = Shape()
    target = _unary(2)

    with pytest.raises(ShapesSearchError, match="explored more than 1"):
        resolve_shapes(
            source,
            target,
            max_depth=2,
            max_visited=1,
        )


def test_search_is_deterministic_for_same_states() -> None:
    source = Shape()
    target = _unary(3)

    first = resolve_shapes(source, target)
    second = resolve_shapes(source, target)

    assert first.steps == second.steps
    assert first.explored == second.explored


def test_deep_unary_one_step_search_is_stack_safe() -> None:
    depth = 128
    source = _unary(depth)
    deepest_leaf = (0,) * depth
    target = add(source, deepest_leaf)

    path = resolve_shapes(
        source,
        target,
        max_depth=1,
        max_nodes=size(target),
        max_visited=1,
    )

    assert path.length == 1
    assert path.steps[0].direction is EditDirection.ADD
    assert path.steps[0].target == deepest_leaf


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"max_depth": -1}, "max_depth must be >= 0"),
        ({"max_nodes": 0}, "max_nodes must be >= 1"),
        ({"max_visited": 0}, "max_visited must be >= 1"),
    ],
)
def test_invalid_bounds_are_rejected(
    kwargs: dict[str, int],
    message: str,
) -> None:
    with pytest.raises(ShapesSearchError, match=message):
        resolve_shapes(Shape(), Shape(), **kwargs)
