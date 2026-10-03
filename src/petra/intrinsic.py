"""Intrinsic PETRA semantics over the retained runtime representation."""

from __future__ import annotations

from .model import Container, Leaf, PetraShape, Root, Term, validate_shape

__all__ = [
    "intrinsic_add",
    "intrinsic_equal",
    "intrinsic_remove",
    "intrinsic_size",
]


def intrinsic_add(
    shape: PetraShape,
    parent_occurrence: tuple[int, ...],
) -> PetraShape:
    """Add one fresh zero-child occurrence at a selected parent occurrence.

    ``parent_occurrence`` is a realization-local selector into the current
    runtime representation. It is operation-local information, not persistent
    PETRA identity.
    """

    validate_shape(shape)
    path = _require_occurrence_path(parent_occurrence)
    selected, frames = _select_occurrence(shape, path)

    if isinstance(selected, Leaf):
        replacement: PetraShape = Container(
            terms=(Term(root=Root(0), exponent=Leaf()),)
        )
    else:
        replacement = Container(
            terms=(
                *selected.terms,
                Term(root=Root(len(selected.terms)), exponent=Leaf()),
            )
        )

    return _rebuild_frames(frames, replacement)


def intrinsic_remove(
    shape: PetraShape,
    leaf_occurrence: tuple[int, ...],
) -> PetraShape:
    """Remove one selected non-root zero-child occurrence.

    ``leaf_occurrence`` is a realization-local selector into the current
    runtime representation. The root occurrence cannot be removed.
    """

    validate_shape(shape)
    path = _require_occurrence_path(leaf_occurrence)
    if not path:
        raise ValueError("intrinsic REMOVE cannot remove the root occurrence")

    selected, frames = _select_occurrence(shape, path)
    if not isinstance(selected, Leaf):
        raise ValueError("intrinsic REMOVE target must be zero-child")

    parent, selected_index = frames[-1]
    remaining = (
        parent.terms[:selected_index]
        + parent.terms[selected_index + 1 :]
    )

    if remaining:
        replacement: PetraShape = Container(
            terms=tuple(
                term
                if term.root.rank == rank
                else Term(root=Root(rank), exponent=term.exponent)
                for rank, term in enumerate(remaining)
            )
        )
    else:
        replacement = Leaf()

    return _rebuild_frames(frames[:-1], replacement)


def intrinsic_equal(left: PetraShape, right: PetraShape) -> bool:
    """Return whether two runtime shapes represent the same PETRA form.

    Runtime sibling order and positional root ranks are representation-level
    data. Intrinsic equality compares the finite rooted non-plane forms while
    preserving child multiplicity.
    """

    validate_shape(left)
    validate_shape(right)

    classes: dict[tuple[int, ...], int] = {}
    left_class = _intrinsic_class_id(left, classes)
    right_class = _intrinsic_class_id(right, classes)
    return left_class == right_class


def intrinsic_size(shape: PetraShape) -> int:
    """Return the number of intrinsic carrier node occurrences in shape."""

    validate_shape(shape)

    total = 0
    pending: list[PetraShape] = [shape]

    while pending:
        current = pending.pop()
        total += 1

        if isinstance(current, Container):
            pending.extend(term.exponent for term in current.terms)

    return total


def _require_occurrence_path(value: object) -> tuple[int, ...]:
    if not isinstance(value, tuple):
        raise TypeError("intrinsic occurrence path must be a tuple")
    if any(type(index) is not int or index < 0 for index in value):
        raise ValueError("intrinsic occurrence path must contain non-negative ints")
    return value


def _select_occurrence(
    shape: PetraShape,
    path: tuple[int, ...],
) -> tuple[PetraShape, list[tuple[Container, int]]]:
    current = shape
    frames: list[tuple[Container, int]] = []

    for index in path:
        if not isinstance(current, Container):
            raise ValueError("intrinsic occurrence path crosses zero-child form")
        if index >= len(current.terms):
            raise ValueError("intrinsic occurrence path is out of range")

        frames.append((current, index))
        current = current.terms[index].exponent

    return current, frames


def _rebuild_frames(
    frames: list[tuple[Container, int]],
    replacement: PetraShape,
) -> PetraShape:
    rebuilt = replacement

    for container, index in reversed(frames):
        terms = list(container.terms)
        selected = terms[index]
        terms[index] = Term(root=selected.root, exponent=rebuilt)
        rebuilt = Container(terms=tuple(terms))

    return rebuilt


def _intrinsic_class_id(
    shape: PetraShape,
    classes: dict[tuple[int, ...], int],
) -> int:
    """Return a call-local structural class id, ignoring sibling order."""

    class_ids: dict[int, int] = {}
    pending: list[tuple[PetraShape, bool]] = [(shape, False)]

    while pending:
        current, expanded = pending.pop()
        current_id = id(current)

        if current_id in class_ids:
            continue

        if isinstance(current, Leaf):
            class_ids[current_id] = _intern_signature((), classes)
            continue

        if not expanded:
            pending.append((current, True))
            for term in current.terms:
                child = term.exponent
                if id(child) not in class_ids:
                    pending.append((child, False))
            continue

        signature = tuple(
            sorted(class_ids[id(term.exponent)] for term in current.terms)
        )
        class_ids[current_id] = _intern_signature(signature, classes)

    return class_ids[id(shape)]


def _intern_signature(
    signature: tuple[int, ...],
    classes: dict[tuple[int, ...], int],
) -> int:
    existing = classes.get(signature)
    if existing is not None:
        return existing

    class_id = len(classes)
    classes[signature] = class_id
    return class_id
