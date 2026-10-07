"""Focused runtime tests for canonical SHAPES -> STR materialization."""

from __future__ import annotations

import pytest

from shapes import Shape, add, iter_occurrences, size
from tensor_view import STR, materialize


def node(*children: Shape) -> Shape:
    return Shape(children=children)


def _enumerate_shapes_through_size(max_size: int) -> dict[int, set[Shape]]:
    by_size: dict[int, set[Shape]] = {1: {Shape()}}

    for current_size in range(1, max_size):
        next_forms: set[Shape] = set()

        for shape in by_size[current_size]:
            assert size(shape) == current_size

            for path, _occurrence in iter_occurrences(shape):
                next_forms.add(add(shape, path))

        by_size[current_size + 1] = next_forms

    return by_size


def _reachable_coordinates(value: STR) -> set[int]:
    reached: set[int] = set()
    pending = [value.root]

    while pending:
        current = pending.pop()

        if current in reached:
            continue

        reached.add(current)

        pending.extend(
            child
            for child, multiplicity in enumerate(
                value.multiplicities[current]
            )
            if multiplicity
        )

    return reached


def _is_acyclic(value: STR) -> bool:
    done: set[int] = set()
    visiting: set[int] = set()
    pending: list[tuple[int, bool]] = [(value.root, False)]

    while pending:
        current, expanded = pending.pop()

        if current in done:
            continue

        if expanded:
            visiting.remove(current)
            done.add(current)
            continue

        if current in visiting:
            return False

        visiting.add(current)
        pending.append((current, True))

        for child, multiplicity in enumerate(
            value.multiplicities[current]
        ):
            if not multiplicity or child in done:
                continue

            if child in visiting:
                return False

            pending.append((child, False))

    return True


def test_zero_form_materializes_to_one_zero_row() -> None:
    assert materialize(Shape()) == STR(
        root=0,
        multiplicities=((0,),),
    )


def test_materialization_preserves_intrinsic_multiplicity() -> None:
    zero = Shape()
    shape = node(zero, zero)

    assert materialize(shape) == STR(
        root=1,
        multiplicities=(
            (0, 0),
            (2, 0),
        ),
    )


def test_equal_subforms_share_one_structural_type_coordinate() -> None:
    zero = Shape()
    unary = node(zero)
    shape = node(unary, unary, zero)

    assert materialize(shape) == STR(
        root=2,
        multiplicities=(
            (0, 0, 0),
            (1, 0, 0),
            (1, 2, 0),
        ),
    )


def test_structural_equality_and_sibling_permutation_give_same_str() -> None:
    zero = Shape()
    unary = node(zero)

    left = node(unary, zero)
    right = node(zero, unary)

    assert left == right
    assert materialize(left) == materialize(right)


def test_materialization_is_deterministic_and_hashable() -> None:
    zero = Shape()
    shape = node(node(zero), zero, zero)

    first = materialize(shape)
    second = materialize(shape)

    assert first == second
    assert hash(first) == hash(second)


def test_materialize_rejects_non_shape_input() -> None:
    with pytest.raises(TypeError, match="expected Shape"):
        materialize(object())  # type: ignore[arg-type]


def test_materialized_coordinates_are_root_reachable_and_acyclic() -> None:
    zero = Shape()
    unary = node(zero)
    shape = node(zero, unary, node(unary))

    value = materialize(shape)
    coordinate_count = len(value.multiplicities)

    assert _reachable_coordinates(value) == set(range(coordinate_count))
    assert _is_acyclic(value)


def test_materialized_matrix_is_square_with_nonnegative_integer_entries() -> None:
    zero = Shape()
    shape = node(zero, node(zero), node(zero, zero))

    value = materialize(shape)
    coordinate_count = len(value.multiplicities)

    assert 0 <= value.root < coordinate_count
    assert all(
        len(row) == coordinate_count
        for row in value.multiplicities
    )
    assert all(
        type(multiplicity) is int and multiplicity >= 0
        for row in value.multiplicities
        for multiplicity in row
    )


def test_distinct_shapes_have_distinct_str_through_size_seven() -> None:
    by_size = _enumerate_shapes_through_size(7)

    assert {
        current_size: len(forms)
        for current_size, forms in by_size.items()
    } == {
        1: 1,
        2: 1,
        3: 2,
        4: 4,
        5: 9,
        6: 20,
        7: 48,
    }

    all_shapes = [
        shape
        for current_size in range(1, 8)
        for shape in by_size[current_size]
    ]

    values = [materialize(shape) for shape in all_shapes]

    assert len(values) == 85
    assert len(set(values)) == len(values)


def test_all_bounded_materializations_satisfy_graph_invariants() -> None:
    by_size = _enumerate_shapes_through_size(7)

    for current_size in range(1, 8):
        for shape in by_size[current_size]:
            value = materialize(shape)
            coordinate_count = len(value.multiplicities)

            assert coordinate_count >= 1
            assert 0 <= value.root < coordinate_count
            assert _reachable_coordinates(value) == set(
                range(coordinate_count)
            )
            assert _is_acyclic(value)


def test_deep_unary_materialization_is_stack_safe_at_2048() -> None:
    shape = Shape()

    for _ in range(2048):
        shape = node(shape)

    value = materialize(shape)

    assert value.root == 2048
    assert len(value.multiplicities) == 2049
    assert value.multiplicities[0][0] == 0
    assert value.multiplicities[1][0] == 1
    assert value.multiplicities[2048][2047] == 1
