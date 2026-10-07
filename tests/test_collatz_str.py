"""M5 conformance tests for the second maintained STR interpreter."""

from __future__ import annotations

from collections import Counter

import pytest

from collatz import interpret_str
from shapes import Shape, add, iter_occurrences
from tensor_view import STR, materialize

EXPECTED_COUNTS = {
    1: 1,
    2: 1,
    3: 2,
    4: 4,
    5: 9,
    6: 20,
    7: 48,
    8: 115,
    9: 286,
    10: 719,
    11: 1842,
}


def _enumerate_shapes_through_size(
    max_size: int,
) -> dict[int, set[Shape]]:
    by_size: dict[int, set[Shape]] = {1: {Shape()}}

    for current_size in range(1, max_size):
        next_forms: set[Shape] = set()

        for shape in by_size[current_size]:
            for path, _occurrence in iter_occurrences(shape):
                next_forms.add(add(shape, path))

        by_size[current_size + 1] = next_forms

    return by_size


def _direct_seed(shape: Shape) -> int:
    """Independent direct SHAPES oracle for the proved seed χ."""

    values: dict[int, int] = {}
    completed: set[int] = set()
    pending: list[tuple[Shape, bool]] = [(shape, False)]

    while pending:
        current, expanded = pending.pop()
        object_id = id(current)

        if object_id in completed:
            continue

        if expanded:
            result = 1
            child_values = Counter(
                values[id(child)]
                for child in current.children
            )

            for child_value, multiplicity in child_values.items():
                result += multiplicity * (child_value + 1) ** 2

            values[object_id] = result
            completed.add(object_id)
            continue

        pending.append((current, True))

        for child in reversed(current.children):
            if id(child) not in completed:
                pending.append((child, False))

    return values[id(shape)]


def test_collatz_str_base_and_first_recursive_values() -> None:
    zero = Shape()
    one_child = Shape(children=(zero,))
    two_zero_children = Shape(children=(zero, zero))
    depth_two_chain = Shape(children=(one_child,))

    assert interpret_str(materialize(zero)) == 1
    assert interpret_str(materialize(one_child)) == 5
    assert interpret_str(materialize(two_zero_children)) == 9
    assert interpret_str(materialize(depth_two_chain)) == 37


def test_collatz_seed_is_not_merely_structural_size() -> None:
    zero = Shape()

    two_zero_children = Shape(children=(zero, zero))
    depth_two_chain = Shape(
        children=(Shape(children=(zero,)),)
    )

    assert interpret_str(materialize(two_zero_children)) == 9
    assert interpret_str(materialize(depth_two_chain)) == 37


def test_collatz_str_is_coordinate_renaming_invariant() -> None:
    canonical = STR(
        root=2,
        multiplicities=(
            (0, 0, 0),
            (1, 0, 0),
            (1, 1, 0),
        ),
    )

    renamed = STR(
        root=0,
        multiplicities=(
            (0, 1, 1),
            (0, 0, 0),
            (0, 1, 0),
        ),
    )

    assert interpret_str(canonical) == interpret_str(renamed)


def test_collatz_rejects_non_str_input() -> None:
    with pytest.raises(TypeError, match="STR value"):
        interpret_str(object())  # type: ignore[arg-type]


def test_collatz_exhaustive_factorization_through_size_eleven() -> None:
    by_size = _enumerate_shapes_through_size(11)

    assert {
        current_size: len(forms)
        for current_size, forms in by_size.items()
    } == EXPECTED_COUNTS

    cases = 0

    for current_size in range(1, 12):
        for shape in by_size[current_size]:
            assert interpret_str(materialize(shape)) == _direct_seed(
                shape
            )
            cases += 1

    assert cases == 3047


def test_collatz_expected_collision_profile_through_size_eleven() -> None:
    by_size = _enumerate_shapes_through_size(11)

    seed_counts: Counter[int] = Counter()

    for current_size in range(1, 12):
        for shape in by_size[current_size]:
            seed_counts[interpret_str(materialize(shape))] += 1

    collision_buckets = sum(
        count > 1
        for count in seed_counts.values()
    )

    assert len(seed_counts) == 2901
    assert collision_buckets == 138
