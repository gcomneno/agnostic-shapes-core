"""Tests for intrinsic PETRA semantics over the runtime representation."""

from __future__ import annotations

import pytest

from petra import (
    Container,
    Leaf,
    Root,
    Term,
    intrinsic_equal,
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
