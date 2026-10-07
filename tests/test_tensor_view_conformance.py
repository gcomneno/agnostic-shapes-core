"""M2 conformance tests for the faithful SHAPES -> STR Tensor View."""

from __future__ import annotations

from collections.abc import Hashable

from shapes import Shape, add, iter_occurrences
from tensor_view import STR, materialize

StructuralSignature = tuple["StructuralSignature", ...]


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


def node(*children: Shape) -> Shape:
    return Shape(children=children)


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


def _shape_signature(shape: Shape) -> StructuralSignature:
    """Derive structural meaning from public Shape.children only."""

    signatures: dict[int, StructuralSignature] = {}
    completed: set[int] = set()
    pending: list[tuple[Shape, bool]] = [(shape, False)]

    while pending:
        current, expanded = pending.pop()
        object_id = id(current)

        if object_id in completed:
            continue

        if expanded:
            signatures[object_id] = tuple(
                sorted(
                    signatures[id(child)]
                    for child in current.children
                )
            )
            completed.add(object_id)
            continue

        pending.append((current, True))

        for child in reversed(current.children):
            if id(child) not in completed:
                pending.append((child, False))

    return signatures[id(shape)]


def _str_signatures(
    value: STR,
) -> tuple[StructuralSignature, ...]:
    """Decode only structural signatures, never runtime Shape values."""

    coordinate_count = len(value.multiplicities)

    signatures: dict[int, StructuralSignature] = {}
    completed: set[int] = set()
    visiting: set[int] = set()
    pending: list[tuple[int, bool]] = [(value.root, False)]

    while pending:
        current, expanded = pending.pop()

        if current in completed:
            continue

        if expanded:
            children: list[StructuralSignature] = []

            for child, multiplicity in enumerate(
                value.multiplicities[current]
            ):
                if not multiplicity:
                    continue

                children.extend(
                    [signatures[child]] * multiplicity
                )

            signatures[current] = tuple(sorted(children))
            visiting.remove(current)
            completed.add(current)
            continue

        if current in visiting:
            raise AssertionError("STR dependency cycle detected")

        visiting.add(current)
        pending.append((current, True))

        for child, multiplicity in enumerate(
            value.multiplicities[current]
        ):
            if not multiplicity or child in completed:
                continue

            if child in visiting:
                raise AssertionError(
                    "STR dependency cycle detected"
                )

            pending.append((child, False))

    if completed != set(range(coordinate_count)):
        raise AssertionError(
            "STR contains a coordinate unreachable from root"
        )

    return tuple(
        signatures[coordinate]
        for coordinate in range(coordinate_count)
    )


def _fresh_copy(shape: Shape) -> Shape:
    """Rebuild an equal form with fresh runtime node objects."""

    copies: dict[int, Shape] = {}
    completed: set[int] = set()
    pending: list[tuple[Shape, bool]] = [(shape, False)]

    while pending:
        current, expanded = pending.pop()
        object_id = id(current)

        if object_id in completed:
            continue

        if expanded:
            copies[object_id] = Shape(
                children=tuple(
                    copies[id(child)]
                    for child in current.children
                )
            )
            completed.add(object_id)
            continue

        pending.append((current, True))

        for child in reversed(current.children):
            if id(child) not in completed:
                pending.append((child, False))

    return copies[id(shape)]


def _assert_basic_str_invariants(value: STR) -> None:
    coordinate_count = len(value.multiplicities)

    assert coordinate_count >= 1
    assert type(value.root) is int
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

    signatures = _str_signatures(value)

    assert len(signatures) == coordinate_count
    assert len(set(signatures)) == coordinate_count


def test_exhaustive_corpus_counts_through_size_eleven() -> None:
    by_size = _enumerate_shapes_through_size(11)

    assert {
        current_size: len(forms)
        for current_size, forms in by_size.items()
    } == EXPECTED_COUNTS

    assert sum(map(len, by_size.values())) == 3047


def test_exhaustive_str_factorization_through_size_eleven() -> None:
    by_size = _enumerate_shapes_through_size(11)

    cases = 0

    for current_size in range(1, 12):
        for shape in by_size[current_size]:
            value = materialize(shape)
            signatures = _str_signatures(value)

            assert signatures[value.root] == _shape_signature(shape)

            cases += 1

    assert cases == 3047


def test_exhaustive_str_faithfulness_through_size_eleven() -> None:
    by_size = _enumerate_shapes_through_size(11)

    values: dict[STR, Shape] = {}

    for current_size in range(1, 12):
        for shape in by_size[current_size]:
            value = materialize(shape)

            previous = values.get(value)

            if previous is not None:
                assert previous == shape

            values[value] = shape

    assert len(values) == 3047


def test_exhaustive_str_invariants_through_size_eleven() -> None:
    by_size = _enumerate_shapes_through_size(11)

    cases = 0

    for current_size in range(1, 12):
        for shape in by_size[current_size]:
            _assert_basic_str_invariants(materialize(shape))
            cases += 1

    assert cases == 3047


def test_exhaustive_materialization_is_allocation_independent() -> None:
    by_size = _enumerate_shapes_through_size(11)

    cases = 0

    for current_size in range(1, 12):
        for shape in by_size[current_size]:
            fresh = _fresh_copy(shape)

            assert fresh == shape
            assert fresh is not shape
            assert materialize(fresh) == materialize(shape)

            cases += 1

    assert cases == 3047


def test_runtime_object_sharing_does_not_change_str() -> None:
    zero = Shape()
    shared_unary = node(zero)

    shared = node(
        shared_unary,
        shared_unary,
        zero,
    )

    copied = node(
        node(Shape()),
        node(Shape()),
        Shape(),
    )

    assert shared == copied
    assert materialize(shared) == materialize(copied)


def test_large_intrinsic_multiplicity_is_preserved_exactly() -> None:
    multiplicity = 4096
    zero = Shape()
    shape = Shape(children=(zero,) * multiplicity)

    value = materialize(shape)

    assert len(value.multiplicities) == 2
    assert value.root == 1
    assert value.multiplicities[0] == (0, 0)
    assert value.multiplicities[1] == (multiplicity, 0)


def test_str_values_are_hashable_runtime_values() -> None:
    shapes = (
        Shape(),
        node(Shape()),
        node(Shape(), Shape()),
        node(node(Shape()), Shape()),
    )

    values: set[Hashable] = {
        materialize(shape)
        for shape in shapes
    }

    assert len(values) == len(shapes)
