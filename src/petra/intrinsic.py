"""Intrinsic PETRA semantics over the retained runtime representation."""

from __future__ import annotations

from .model import Container, Leaf, PetraShape, validate_shape

__all__ = ["intrinsic_equal", "intrinsic_size"]


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
