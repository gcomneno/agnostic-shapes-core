"""Faithful structural materialization of SHAPES forms into STR."""

from __future__ import annotations

from dataclasses import dataclass

from shapes import Shape, validate


@dataclass(frozen=True, slots=True)
class STR:
    """One canonical runtime representative of a Structural Tensor Representation.

    ``root`` is the local coordinate of the complete input structural type.

    ``multiplicities[i][j]`` is the multiplicity of child structural type
    ``j`` under parent structural type ``i``.

    Coordinate numbers are local representation metadata only. They are not
    persistent structural identities.
    """

    root: int
    multiplicities: tuple[tuple[int, ...], ...]


def materialize(shape: Shape) -> STR:
    """Materialize one SHAPES form as a deterministic canonical STR value.

    The implementation derives structural types from public recursive SHAPES
    structure. It does not depend on ``Shape._key`` and does not use Python
    recursion.
    """

    validate(shape)

    postorder = _postorder_nodes(shape)

    height_by_object: dict[int, int] = {}
    nodes_by_height: dict[int, list[Shape]] = {}

    for current in postorder:
        object_id = id(current)

        if current.children:
            current_height = 1 + max(
                height_by_object[id(child)]
                for child in current.children
            )
        else:
            current_height = 0

        height_by_object[object_id] = current_height
        nodes_by_height.setdefault(current_height, []).append(current)

    type_by_object: dict[int, int] = {}
    representative_by_type: dict[int, Shape] = {}
    next_coordinate = 0

    for current_height in range(max(nodes_by_height) + 1):
        classes: dict[tuple[int, ...], list[Shape]] = {}

        for current in nodes_by_height.get(current_height, []):
            descriptor = tuple(
                sorted(
                    type_by_object[id(child)]
                    for child in current.children
                )
            )
            classes.setdefault(descriptor, []).append(current)

        for descriptor in sorted(classes):
            coordinate = next_coordinate
            next_coordinate += 1

            members = classes[descriptor]
            representative_by_type[coordinate] = members[0]

            for member in members:
                type_by_object[id(member)] = coordinate

    coordinate_count = next_coordinate
    rows: list[tuple[int, ...]] = []

    for coordinate in range(coordinate_count):
        representative = representative_by_type[coordinate]
        counts = [0] * coordinate_count

        for child in representative.children:
            counts[type_by_object[id(child)]] += 1

        rows.append(tuple(counts))

    return STR(
        root=type_by_object[id(shape)],
        multiplicities=tuple(rows),
    )


def _postorder_nodes(shape: Shape) -> list[Shape]:
    """Return unique runtime node objects in child-before-parent order."""

    order: list[Shape] = []
    completed: set[int] = set()
    pending: list[tuple[Shape, bool]] = [(shape, False)]

    while pending:
        current, expanded = pending.pop()
        object_id = id(current)

        if object_id in completed:
            continue

        if expanded:
            order.append(current)
            completed.add(object_id)
            continue

        pending.append((current, True))

        for child in reversed(current.children):
            if id(child) not in completed:
                pending.append((child, False))

    return order
