"""COLLATZ structural interpretation over STR."""

from __future__ import annotations

from tensor_view import STR


def interpret_str(value: STR) -> int:
    """Evaluate the proved COLLATZ structural seed directly from STR."""

    if not isinstance(value, STR):
        raise TypeError("COLLATZ input must be an STR value")

    interpreted: dict[int, int] = {}
    completed: set[int] = set()
    visiting: set[int] = set()
    pending: list[tuple[int, bool]] = [(value.root, False)]

    while pending:
        current, expanded = pending.pop()

        if current in completed:
            continue

        row = value.multiplicities[current]

        if expanded:
            result = 1

            for child, multiplicity in enumerate(row):
                if not multiplicity:
                    continue

                child_value = interpreted[child]
                result += multiplicity * (child_value + 1) ** 2

            interpreted[current] = result
            visiting.remove(current)
            completed.add(current)
            continue

        if current in visiting:
            raise ValueError("STR dependency graph must be acyclic")

        visiting.add(current)
        pending.append((current, True))

        for child, multiplicity in reversed(tuple(enumerate(row))):
            if not multiplicity or child in completed:
                continue

            if child in visiting:
                raise ValueError("STR dependency graph must be acyclic")

            pending.append((child, False))

    return interpreted[value.root]
