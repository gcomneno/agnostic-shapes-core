"""Interpretation-agnostic structural core for finite rooted non-plane forms."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TypeAlias

OccurrencePath: TypeAlias = tuple[int, ...]


@dataclass(frozen=True, slots=True, eq=False)
class Shape:
    """One finite rooted non-plane form.

    ``children`` is a concrete immutable representation of the root's child
    multiset. Construction canonicalizes sibling order, so tuple position does
    not participate in structural equality. Equal children remain repeated and
    therefore preserve multiplicity.

    Canonical tuple order is a representation detail only. Occurrence paths
    are valid only against the concrete Shape state from which they were
    obtained.
    """

    children: tuple[Shape, ...] = ()
    _key: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.children, tuple):
            raise TypeError("shape children must be a tuple")

        if any(not isinstance(child, Shape) for child in self.children):
            raise TypeError("shape children must contain only Shape values")

        canonical = tuple(sorted(self.children, key=lambda child: child._key))

        if canonical != self.children:
            object.__setattr__(self, "children", canonical)

        object.__setattr__(
            self,
            "_key",
            "(" + "".join(child._key for child in canonical) + ")",
        )

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True

        if not isinstance(other, Shape):
            return NotImplemented

        return self._key == other._key

    def __hash__(self) -> int:
        return hash(self._key)


def size(shape: Shape) -> int:
    """Return the number of node occurrences in ``shape``."""

    validate(shape)

    total = 0
    pending = [shape]

    while pending:
        current = pending.pop()
        total += 1
        pending.extend(current.children)

    return total


def height(shape: Shape) -> int:
    """Return the maximum occurrence depth, with the root at depth zero."""

    validate(shape)

    best = 0
    pending: list[tuple[Shape, int]] = [(shape, 0)]

    while pending:
        current, depth = pending.pop()
        best = max(best, depth)
        pending.extend((child, depth + 1) for child in current.children)

    return best


def leaf_count(shape: Shape) -> int:
    """Return the number of zero-child occurrences in ``shape``."""

    validate(shape)

    total = 0
    pending = [shape]

    while pending:
        current = pending.pop()

        if current.children:
            pending.extend(current.children)
        else:
            total += 1

    return total


def add(shape: Shape, parent: OccurrencePath) -> Shape:
    """Add one fresh zero-child occurrence below ``parent``.

    ``parent`` is an operation-local selector into the current canonical
    realization. It is not persistent identity and is not part of Shape
    equality.
    """

    validate(shape)
    path = _require_occurrence_path(parent)
    selected, frames = _select_occurrence(shape, path)

    replacement = Shape(children=(*selected.children, Shape()))
    return _rebuild_frames(frames, replacement)


def remove(shape: Shape, leaf: OccurrencePath) -> Shape:
    """Remove one selected zero-child non-root occurrence."""

    validate(shape)
    path = _require_occurrence_path(leaf)

    if not path:
        raise ValueError("REMOVE cannot remove the root occurrence")

    selected, frames = _select_occurrence(shape, path)

    if selected.children:
        raise ValueError("REMOVE target must be zero-child")

    parent, selected_index = frames[-1]
    remaining = (
        parent.children[:selected_index]
        + parent.children[selected_index + 1 :]
    )
    replacement = Shape(children=remaining)

    return _rebuild_frames(frames[:-1], replacement)


def validate(shape: object) -> None:
    """Validate a SHAPES value and its canonical structural representation."""

    if not isinstance(shape, Shape):
        raise TypeError("expected Shape")

    pending = [shape]

    while pending:
        current = pending.pop()

        if not isinstance(current.children, tuple):
            raise TypeError("shape children must be a tuple")

        if any(not isinstance(child, Shape) for child in current.children):
            raise TypeError("shape children must contain only Shape values")

        canonical = tuple(
            sorted(current.children, key=lambda child: child._key)
        )
        if canonical != current.children:
            raise ValueError(
                "shape children are not in canonical structural order"
            )

        expected_key = (
            "(" + "".join(child._key for child in current.children) + ")"
        )
        if current._key != expected_key:
            raise ValueError("shape structural key is inconsistent")

        pending.extend(current.children)



def iter_occurrences(
    shape: Shape,
) -> Iterator[tuple[OccurrencePath, Shape]]:
    """Yield every occurrence with its path in the current canonical state.

    Traversal is deterministic preorder over the concrete canonical tuple
    representation. Paths are operation-local, state-scoped selectors only;
    they are not persistent occurrence identity across edited forms.

    Structurally equal sibling occurrences remain distinct traversal entries
    because each child incidence has its own path in the current realization.
    """

    validate(shape)

    pending: list[tuple[OccurrencePath, Shape]] = [((), shape)]

    while pending:
        path, current = pending.pop()
        yield path, current

        for index in range(len(current.children) - 1, -1, -1):
            pending.append(((*path, index), current.children[index]))


def _require_occurrence_path(value: object) -> OccurrencePath:
    if not isinstance(value, tuple):
        raise TypeError("occurrence path must be a tuple")

    if any(type(index) is not int or index < 0 for index in value):
        raise ValueError(
            "occurrence path must contain non-negative integer indices"
        )

    return value


def _select_occurrence(
    shape: Shape,
    path: OccurrencePath,
) -> tuple[Shape, list[tuple[Shape, int]]]:
    current = shape
    frames: list[tuple[Shape, int]] = []

    for index in path:
        if not current.children:
            raise ValueError("occurrence path crosses zero-child form")

        if index >= len(current.children):
            raise ValueError("occurrence path is out of range")

        frames.append((current, index))
        current = current.children[index]

    return current, frames


def _rebuild_frames(
    frames: list[tuple[Shape, int]],
    replacement: Shape,
) -> Shape:
    rebuilt = replacement

    for parent, index in reversed(frames):
        children = list(parent.children)
        children[index] = rebuilt
        rebuilt = Shape(children=tuple(children))

    return rebuilt
