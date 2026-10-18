"""M4 runtime equivalence gate for direct and STR-based LRPE evaluation."""

from __future__ import annotations

from petra import (
    LRPE,
    MaterializationLimitError,
    MaterializationLimits,
)
from shapes import Shape, add, iter_occurrences
from tensor_view import materialize

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


def _direct_outcome(
    shape: Shape,
    limits: MaterializationLimits,
) -> tuple[str, int | str]:
    try:
        return ("value", LRPE.interpret(shape, limits=limits))
    except MaterializationLimitError as exc:
        return ("limit", str(exc))


def _str_outcome(
    shape: Shape,
    limits: MaterializationLimits,
) -> tuple[str, int | str]:
    try:
        return (
            "value",
            LRPE.interpret_str(
                materialize(shape),
                limits=limits,
            ),
        )
    except MaterializationLimitError as exc:
        return ("limit", str(exc))


def test_m4_corpus_is_complete_through_size_eleven() -> None:
    by_size = _enumerate_shapes_through_size(11)

    assert {
        current_size: len(forms)
        for current_size, forms in by_size.items()
    } == EXPECTED_COUNTS

    assert sum(map(len, by_size.values())) == 3047


def test_m4_max_value_behavior_agrees_on_all_3047_shapes() -> None:
    by_size = _enumerate_shapes_through_size(11)
    limits = MaterializationLimits(max_value=1_000_000)

    cases = 0
    materialized = 0
    limited = 0

    for current_size in range(1, 12):
        for shape in by_size[current_size]:
            direct = _direct_outcome(shape, limits)
            through_str = _str_outcome(shape, limits)

            assert through_str == direct

            if direct[0] == "value":
                materialized += 1

                direct_unbounded = LRPE.interpret(shape)
                str_unbounded = LRPE.interpret_str(
                    materialize(shape)
                )

                assert direct_unbounded == str_unbounded
                assert direct_unbounded == direct[1]
            else:
                limited += 1

            cases += 1

    assert cases == 3047
    assert materialized > 0
    assert limited > 0


def test_m4_max_exponent_behavior_agrees_on_all_3047_shapes() -> None:
    by_size = _enumerate_shapes_through_size(11)
    limits = MaterializationLimits(max_exponent=4096)

    cases = 0
    materialized = 0
    limited = 0

    for current_size in range(1, 12):
        for shape in by_size[current_size]:
            direct = _direct_outcome(shape, limits)
            through_str = _str_outcome(shape, limits)

            assert through_str == direct

            if direct[0] == "value":
                materialized += 1
            else:
                limited += 1

            cases += 1

    assert cases == 3047
    assert materialized > 0
    assert limited > 0


def test_m4_combined_limits_agree_on_all_3047_shapes() -> None:
    by_size = _enumerate_shapes_through_size(11)
    limits = MaterializationLimits(
        max_exponent=4096,
        max_value=1_000_000,
    )

    cases = 0

    materialized = 0
    limited = 0

    for current_size in range(1, 12):
        for shape in by_size[current_size]:
            direct = _direct_outcome(shape, limits)
            through_str = _str_outcome(shape, limits)

            assert through_str[0] == direct[0]

            if direct[0] == "value":
                assert through_str[1] == direct[1]
                materialized += 1
            else:
                limited += 1

            cases += 1

    assert cases == 3047
    assert materialized > 0
    assert limited > 0
