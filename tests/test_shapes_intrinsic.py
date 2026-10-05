"""Tests for the interpretation-agnostic SHAPES intrinsic core."""

from __future__ import annotations

import pytest

from shapes import (
    Shape,
    add,
    height,
    iter_occurrences,
    leaf_count,
    remove,
    size,
    validate,
)


def node(*children: Shape) -> Shape:
    return Shape(children=children)


def test_zero_child_form_has_size_one() -> None:
    zero = Shape()

    assert zero.children == ()
    assert size(zero) == 1


def test_size_preserves_child_multiplicity() -> None:
    shared = node(Shape())
    shape = node(shared, shared)

    assert size(shape) == 5


def test_sibling_permutation_does_not_change_structural_equality() -> None:
    zero = Shape()
    unary = node(zero)

    left = node(unary, zero)
    right = node(zero, unary)

    assert left == right
    assert hash(left) == hash(right)
    assert left.children == right.children


def test_different_child_multiplicity_changes_the_form() -> None:
    zero = Shape()

    assert node(zero, zero) != node(zero)


def test_structural_equality_is_recursive_and_order_independent() -> None:
    zero = Shape()
    unary = node(zero)

    left = node(node(zero, unary), zero)
    right = node(zero, node(unary, zero))

    assert left == right


def test_zero_child_form_has_intrinsic_height_and_leaf_count() -> None:
    zero = Shape()

    assert height(zero) == 0
    assert leaf_count(zero) == 1


def test_intrinsic_metrics_preserve_occurrence_multiplicity() -> None:
    zero = Shape()
    unary = node(zero)
    shape = node(unary, unary, zero)

    assert height(shape) == 2
    assert leaf_count(shape) == 3


def test_intrinsic_metrics_are_invariant_under_structural_equality() -> None:
    zero = Shape()
    unary = node(zero)

    left = node(unary, zero)
    right = node(zero, unary)

    assert left == right
    assert height(left) == height(right) == 2
    assert leaf_count(left) == leaf_count(right) == 2


def test_intrinsic_metrics_have_expected_one_step_add_cases() -> None:
    zero = Shape()
    unary = node(zero)

    add_below_leaf = add(zero, ())
    assert height(add_below_leaf) == height(zero) + 1
    assert leaf_count(add_below_leaf) == leaf_count(zero)

    add_below_non_leaf = add(unary, ())
    assert height(add_below_non_leaf) == height(unary)
    assert leaf_count(add_below_non_leaf) == leaf_count(unary) + 1


def test_intrinsic_metrics_have_expected_one_step_remove_cases() -> None:
    zero = Shape()

    wider_parent = node(zero, zero)
    one_leaf_path = next(
        path
        for path, occurrence in iter_occurrences(wider_parent)
        if path and not occurrence.children
    )
    after_wider_remove = remove(wider_parent, one_leaf_path)

    assert abs(height(after_wider_remove) - height(wider_parent)) <= 1
    assert leaf_count(after_wider_remove) == leaf_count(wider_parent) - 1

    unary = node(zero)
    after_only_child_remove = remove(unary, (0,))

    assert height(after_only_child_remove) == height(unary) - 1
    assert leaf_count(after_only_child_remove) == leaf_count(unary)


def test_add_at_root_changes_size_by_one() -> None:
    before = Shape()

    after = add(before, ())

    assert size(after) == size(before) + 1
    assert after == node(Shape())


def test_add_at_nested_occurrence_is_local() -> None:
    before = node(node(Shape()))

    after = add(before, (0, 0))

    assert after == node(node(node(Shape())))
    assert size(after) == size(before) + 1


def test_remove_changes_size_by_one() -> None:
    zero = Shape()
    before = node(zero, node(zero), zero)

    leaf_index = next(
        index
        for index, child in enumerate(before.children)
        if not child.children
    )

    after = remove(before, (leaf_index,))

    assert after == node(zero, node(zero))
    assert size(after) == size(before) - 1


def test_pointed_add_and_remove_are_converse_on_forms() -> None:
    zero = Shape()
    before = node(node(zero), zero)

    after_add = add(before, ())
    fresh_equivalent_leaf = next(
        index
        for index, child in enumerate(after_add.children)
        if not child.children
    )
    restored = remove(after_add, (fresh_equivalent_leaf,))

    assert restored == before


def test_every_constructed_chain_reduces_to_zero_child_form() -> None:
    zero = Shape()

    one = add(zero, ())
    two = add(one, (0,))

    assert remove(two, (0, 0)) == one
    assert remove(one, (0,)) == zero


def test_remove_rejects_root_and_non_zero_child_target() -> None:
    zero = Shape()
    unary = node(zero)

    with pytest.raises(ValueError, match="cannot remove the root"):
        remove(unary, ())

    non_leaf_target = node(unary)
    with pytest.raises(ValueError, match="target must be zero-child"):
        remove(non_leaf_target, (0,))


def test_occurrence_paths_are_state_scoped_and_validated() -> None:
    zero = Shape()
    unary = node(zero)

    assert add(unary, (0,)) == node(node(zero))

    with pytest.raises(ValueError, match="crosses zero-child"):
        add(zero, (0,))

    with pytest.raises(ValueError, match="out of range"):
        add(unary, (1,))

    with pytest.raises(TypeError, match="must be a tuple"):
        add(unary, [0])  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="non-negative integer"):
        add(unary, (-1,))


def test_constructor_and_validation_reject_non_shape_children() -> None:
    validate(Shape())

    with pytest.raises(TypeError, match="children must be a tuple"):
        Shape(children=[Shape()])  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="only Shape"):
        Shape(children=(object(),))  # type: ignore[arg-type]


def deep_unary(depth: int) -> Shape:
    shape = Shape()

    for _ in range(depth):
        shape = node(shape)

    return shape


def test_deep_unary_shapes_are_stack_safe_at_2048() -> None:
    left = deep_unary(2048)
    right = deep_unary(2048)
    leaf_path = (0,) * 2048

    assert size(left) == 2049
    assert height(left) == 2048
    assert leaf_count(left) == 1
    assert left == right
    assert hash(left) == hash(right)
    assert size(add(left, leaf_path)) == 2050
    assert remove(left, leaf_path) == deep_unary(2047)


def test_add_to_equal_sibling_occurrences_has_same_form() -> None:
    unary = node(Shape())
    before = node(unary, unary)

    assert add(before, (0,)) == add(before, (1,))


def test_paths_are_state_scoped_after_recanonicalization() -> None:
    zero = Shape()
    unary = node(zero)
    before = node(zero, zero)

    stale_path = (1,)
    after = add(before, stale_path)

    assert after == node(unary, zero)
    assert after.children == (unary, zero)

    reused_stale_path = add(after, stale_path)
    current_edited_path = add(after, (0,))

    assert reused_stale_path == node(unary, unary)
    assert current_edited_path == node(node(zero, zero), zero)
    assert reused_stale_path != current_edited_path


def test_iter_occurrences_yields_root_and_nested_paths() -> None:
    zero = Shape()
    unary = node(zero)
    shape = node(unary, zero)

    occurrences = list(iter_occurrences(shape))

    assert occurrences == [
        ((), shape),
        ((0,), unary),
        ((0, 0), zero),
        ((1,), zero),
    ]


def test_iter_occurrences_preserves_duplicate_occurrences() -> None:
    zero = Shape()
    shape = node(zero, zero)

    occurrences = list(iter_occurrences(shape))

    assert occurrences == [
        ((), shape),
        ((0,), zero),
        ((1,), zero),
    ]
    assert occurrences[1][1] == occurrences[2][1]


def test_iter_occurrence_paths_are_valid_add_targets() -> None:
    zero = Shape()
    before = node(node(zero), zero)

    paths = [
        path
        for path, _ in iter_occurrences(before)
    ]

    after_forms = {
        add(before, path)
        for path in paths
    }

    assert size(after_forms.pop()) == size(before) + 1
    assert all(
        size(after) == size(before) + 1
        for after in after_forms
    )


def test_iter_occurrence_paths_select_removable_zero_child_occurrences() -> None:
    zero = Shape()
    before = node(node(zero), zero)

    leaf_paths = [
        path
        for path, occurrence in iter_occurrences(before)
        if path and not occurrence.children
    ]

    assert leaf_paths == [(0, 0), (1,)]

    after_forms = [
        remove(before, path)
        for path in leaf_paths
    ]

    assert all(
        size(after) == size(before) - 1
        for after in after_forms
    )


def test_iter_occurrence_paths_must_be_rederived_after_edit() -> None:
    zero = Shape()
    before = node(zero, zero)

    before_paths = [
        path
        for path, _ in iter_occurrences(before)
    ]

    after = add(before, (1,))

    after_occurrences = dict(iter_occurrences(after))

    assert before_paths == [(), (0,), (1,)]
    assert after_occurrences[(0,)] == node(zero)
    assert after_occurrences[(1,)] == zero

    reused_old_path = add(after, (1,))
    current_nested_path = add(after, (0,))

    assert reused_old_path != current_nested_path



def test_iter_occurrences_count_equals_intrinsic_size() -> None:
    zero = Shape()
    shared = node(zero)
    shape = node(shared, shared, zero)

    occurrences = list(iter_occurrences(shape))

    assert len(occurrences) == size(shape)
