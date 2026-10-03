"""Tests for intrinsic PETRA semantics over the runtime representation."""

from __future__ import annotations

import pytest

from petra import (
    Container,
    Leaf,
    Root,
    Term,
    intrinsic_add,
    intrinsic_equal,
    intrinsic_remove,
    intrinsic_size,
    node_count,
)


def container(*children: object) -> Container:
    return Container(
        terms=tuple(
            Term(root=Root(rank), exponent=child)
            for rank, child in enumerate(children)
        )
    )


def unary(child: object) -> Container:
    return container(child)


def deep_unary(depth: int) -> object:
    shape: object = Leaf()
    for _ in range(depth):
        shape = unary(shape)
    return shape


def test_intrinsic_size_counts_carrier_occurrences_not_representation_nodes() -> None:
    shape = container(Leaf(), Leaf())

    assert intrinsic_size(shape) == 3
    assert node_count(shape) == 5


def test_intrinsic_size_counts_reused_subshape_per_occurrence() -> None:
    shared = unary(Leaf())
    shape = container(shared, shared)

    assert intrinsic_size(shape) == 5


def test_intrinsic_equal_ignores_sibling_order_and_positional_ranks() -> None:
    unary_child = unary(Leaf())
    left = container(unary_child, Leaf())
    right = container(Leaf(), unary_child)

    assert left != right
    assert intrinsic_equal(left, right)


def test_intrinsic_equal_preserves_child_multiplicity() -> None:
    left = container(Leaf(), Leaf())
    right = container(Leaf(), unary(Leaf()))

    assert not intrinsic_equal(left, right)


def test_intrinsic_equal_is_recursive_and_order_independent() -> None:
    left = container(
        container(Leaf(), unary(Leaf())),
        Leaf(),
    )
    right = container(
        Leaf(),
        container(unary(Leaf()), Leaf()),
    )

    assert intrinsic_equal(left, right)


def test_intrinsic_operations_require_valid_runtime_shapes() -> None:
    malformed = Container(
        terms=(Term(root=Root(1), exponent=Leaf()),)
    )

    with pytest.raises(ValueError, match="non-canonical root rank"):
        intrinsic_size(malformed)

    with pytest.raises(ValueError, match="non-canonical root rank"):
        intrinsic_equal(malformed, Leaf())


def test_intrinsic_semantics_are_stack_safe_at_supported_depth() -> None:
    left = deep_unary(2048)
    right = deep_unary(2048)

    assert intrinsic_size(left) == 2049  # type: ignore[arg-type]
    assert intrinsic_equal(left, right)  # type: ignore[arg-type]


def test_intrinsic_add_at_root_changes_size_by_one() -> None:
    before = Leaf()

    after = intrinsic_add(before, ())

    assert intrinsic_size(after) == intrinsic_size(before) + 1
    assert after == unary(Leaf())


def test_intrinsic_add_at_nested_occurrence_is_local() -> None:
    before = container(unary(Leaf()), Leaf())

    after = intrinsic_add(before, (0, 0))

    expected = container(
        container(unary(Leaf())),
        Leaf(),
    )
    assert after == expected
    assert intrinsic_size(after) == intrinsic_size(before) + 1


def test_intrinsic_remove_changes_size_by_one_and_closes_ranks() -> None:
    before = container(
        Leaf(),
        unary(Leaf()),
        Leaf(),
    )

    after = intrinsic_remove(before, (0,))

    expected = container(
        unary(Leaf()),
        Leaf(),
    )
    assert after == expected
    assert intrinsic_size(after) == intrinsic_size(before) - 1


def test_pointed_add_then_remove_restores_representation() -> None:
    before = container(unary(Leaf()), Leaf())
    parent = (0,)

    after_add = intrinsic_add(before, parent)
    fresh_child = (*parent, 1)
    restored = intrinsic_remove(after_add, fresh_child)

    assert restored == before


def test_remove_then_add_restores_intrinsic_form_not_order() -> None:
    unary_child = unary(Leaf())
    before = container(Leaf(), unary_child)

    after_remove = intrinsic_remove(before, (0,))
    restored = intrinsic_add(after_remove, ())

    assert restored != before
    assert intrinsic_equal(restored, before)


def test_intrinsic_remove_rejects_root_or_non_leaf_target() -> None:
    shape = unary(Leaf())

    with pytest.raises(
        ValueError,
        match="cannot remove the root occurrence",
    ):
        intrinsic_remove(shape, ())

    non_leaf_target = container(unary(Leaf()))
    with pytest.raises(
        ValueError,
        match="target must be zero-child",
    ):
        intrinsic_remove(non_leaf_target, (0,))


def test_intrinsic_edit_paths_are_realization_local_and_validated() -> None:
    shape = unary(Leaf())

    with pytest.raises(ValueError, match="out of range"):
        intrinsic_add(shape, (1,))

    with pytest.raises(ValueError, match="crosses zero-child"):
        intrinsic_add(shape, (0, 0))

    with pytest.raises(TypeError, match="must be a tuple"):
        intrinsic_add(shape, [0])  # type: ignore[arg-type]
