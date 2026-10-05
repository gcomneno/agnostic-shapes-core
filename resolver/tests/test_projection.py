"""Tests for the legacy PETRA projection layer."""

from __future__ import annotations

import pytest
from petra import parse_shape

from resolver.projection import PrimeKey, ProjectionError, project


def test_project_wide_shape() -> None:
    shape = parse_shape("C(r0^1,r1^1)")
    key = PrimeKey({(0,): 2, (1,): 3})

    assert project(shape, key) == 6


def test_project_nested_exponent() -> None:
    shape = parse_shape("C(r0^C(r0^1),r1^C(r0^1))")
    key = PrimeKey(
        {
            (0,): 2,
            (0, 0): 2,
            (1,): 3,
            (1, 0): 5,
        }
    )

    assert project(shape, key) == 972


def test_project_primorial() -> None:
    shape = parse_shape("C(r0^1,r1^1,r2^1,r3^1,r4^1,r5^1)")
    key = PrimeKey(
        {
            (0,): 2,
            (1,): 3,
            (2,): 5,
            (3,): 7,
            (4,): 11,
            (5,): 13,
        }
    )

    assert project(shape, key) == 30030


def test_project_missing_assignment_raises() -> None:
    shape = parse_shape("C(r0^1,r1^1)")
    key = PrimeKey({(0,): 2})

    with pytest.raises(ProjectionError):
        project(shape, key)


@pytest.mark.parametrize(
    ("assignments", "exception"),
    [
        ({(0,): 1}, ValueError),
        ({(0,): 0}, ValueError),
        ({(0,): -3}, ValueError),
        ({(0,): 2.5}, TypeError),
        ({("a",): 2}, TypeError),
        ({(-1,): 2}, ValueError),
    ],
)
def test_prime_key_rejects_invalid_assignments(
    assignments: dict, exception: type[Exception]
) -> None:
    with pytest.raises(exception):
        PrimeKey(assignments)
