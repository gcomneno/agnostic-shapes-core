import pytest

from petra import (
    LRPE,
    MaterializationLimitError,
    MaterializationLimits,
    ReverseDomainError,
)
from shapes import Shape, add, iter_occurrences, size


def _enumerate_shapes_through_size(max_size: int) -> dict[int, set[Shape]]:
    by_size: dict[int, set[Shape]] = {1: {Shape()}}

    for current_size in range(1, max_size):
        next_forms: set[Shape] = set()

        for shape in by_size[current_size]:
            assert size(shape) == current_size

            for path, _occurrence in iter_occurrences(shape):
                next_forms.add(add(shape, path))

        by_size[current_size + 1] = next_forms

    return by_size


def test_policy_identity_is_explicit() -> None:
    assert LRPE.name == "lrpe"


def test_lrpe_base_and_first_recursive_values() -> None:
    zero = Shape()
    one_child = Shape(children=(zero,))
    two_zero_children = Shape(children=(zero, zero))
    depth_two_chain = Shape(children=(one_child,))

    assert LRPE.interpret(zero) == 1
    assert LRPE.interpret(one_child) == 2
    assert LRPE.interpret(two_zero_children) == 4
    assert LRPE.interpret(depth_two_chain) == 8


def test_lrpe_repairs_pip_2_collision() -> None:
    zero = Shape()
    one_child = Shape(children=(zero,))

    two_zero_children = Shape(children=(zero, zero))
    depth_two_chain = Shape(children=(one_child,))

    assert two_zero_children != depth_two_chain
    assert LRPE.interpret(two_zero_children) == 4
    assert LRPE.interpret(depth_two_chain) == 8


def test_lrpe_round_trip_for_distinct_child_classes() -> None:
    zero = Shape()
    one_child = Shape(children=(zero,))
    shape = Shape(children=(zero, one_child))

    value = LRPE.interpret(shape)

    assert value == 24
    assert LRPE.reverse(value) == shape


@pytest.mark.parametrize(
    "shape",
    [
        Shape(),
        Shape(children=(Shape(),)),
        Shape(children=(Shape(), Shape())),
        Shape(children=(Shape(children=(Shape(),)),)),
        Shape(
            children=(
                Shape(),
                Shape(children=(Shape(),)),
            )
        ),
    ],
)
def test_lrpe_round_trip(shape: Shape) -> None:
    assert LRPE.reverse(LRPE.interpret(shape)) == shape




def test_lrpe_bounded_exhaustive_conformance() -> None:
    """Corroborate LRPE runtime behavior without replacing the PIP proof."""

    by_size = _enumerate_shapes_through_size(5)

    assert {
        current_size: len(forms)
        for current_size, forms in by_size.items()
    } == {
        1: 1,
        2: 1,
        3: 2,
        4: 4,
        5: 9,
    }

    values: list[int] = []

    for current_size in range(1, 6):
        for shape in by_size[current_size]:
            value = LRPE.interpret(shape)

            assert LRPE.reverse(value) == shape
            values.append(value)

    assert len(values) == 17
    assert len(values) == len(set(values))


def test_lrpe_rejects_unreachable_three() -> None:
    with pytest.raises(ReverseDomainError):
        LRPE.reverse(3)


def test_lrpe_rejects_prime_support_gap() -> None:
    with pytest.raises(ReverseDomainError):
        LRPE.reverse(10)


def test_lrpe_reverse_requires_positive_integer() -> None:
    with pytest.raises(TypeError):
        LRPE.reverse(True)

    with pytest.raises(ValueError):
        LRPE.reverse(0)


def test_lrpe_max_exponent_is_runtime_limit_not_domain_failure() -> None:
    zero = Shape()
    two_zero_children = Shape(children=(zero, zero))

    with pytest.raises(MaterializationLimitError):
        LRPE.interpret(
            two_zero_children,
            limits=MaterializationLimits(max_exponent=1),
        )


def test_lrpe_max_value_is_runtime_limit_not_domain_failure() -> None:
    zero = Shape()
    depth_two_chain = Shape(children=(Shape(children=(zero,)),))

    assert LRPE.interpret(depth_two_chain) == 8

    with pytest.raises(MaterializationLimitError):
        LRPE.interpret(
            depth_two_chain,
            limits=MaterializationLimits(max_value=7),
        )


@pytest.mark.parametrize(
    ("kwargs", "name"),
    [
        ({"max_exponent": 0}, "max_exponent"),
        ({"max_value": 0}, "max_value"),
    ],
)
def test_materialization_limits_require_positive_values(
    kwargs: dict[str, int],
    name: str,
) -> None:
    with pytest.raises(ValueError, match=name):
        MaterializationLimits(**kwargs)


def test_lrpe_deep_forward_reports_materialization_limit_not_recursion_error() -> None:
    shape = Shape()

    for _ in range(1500):
        shape = Shape(children=(shape,))

    with pytest.raises(MaterializationLimitError):
        LRPE.interpret(
            shape,
            limits=MaterializationLimits(max_exponent=1),
        )


def test_lrpe_interpret_str_base_and_recursive_values() -> None:
    from tensor_view import materialize

    zero = Shape()
    one_child = Shape(children=(zero,))
    two_zero_children = Shape(children=(zero, zero))
    depth_two_chain = Shape(children=(one_child,))

    assert LRPE.interpret_str(materialize(zero)) == 1
    assert LRPE.interpret_str(materialize(one_child)) == 2
    assert LRPE.interpret_str(materialize(two_zero_children)) == 4
    assert LRPE.interpret_str(materialize(depth_two_chain)) == 8


def test_lrpe_interpret_str_does_not_require_shape_decoder() -> None:
    from tensor_view import STR

    value = STR(
        root=2,
        multiplicities=(
            (0, 0, 0),
            (1, 0, 0),
            (1, 1, 0),
        ),
    )

    assert LRPE.interpret_str(value) == 24


def test_lrpe_interpret_str_is_coordinate_renaming_invariant() -> None:
    from tensor_view import STR

    canonical = STR(
        root=2,
        multiplicities=(
            (0, 0, 0),
            (1, 0, 0),
            (1, 1, 0),
        ),
    )

    renamed = STR(
        root=0,
        multiplicities=(
            (0, 1, 1),
            (0, 0, 0),
            (0, 1, 0),
        ),
    )

    assert LRPE.interpret_str(canonical) == 24
    assert LRPE.interpret_str(renamed) == 24


def test_lrpe_interpret_str_preserves_materialization_limits() -> None:
    from tensor_view import STR

    two_zero_children = STR(
        root=1,
        multiplicities=(
            (0, 0),
            (2, 0),
        ),
    )

    with pytest.raises(MaterializationLimitError):
        LRPE.interpret_str(
            two_zero_children,
            limits=MaterializationLimits(max_exponent=1),
        )

    depth_two_chain = STR(
        root=2,
        multiplicities=(
            (0, 0, 0),
            (1, 0, 0),
            (0, 1, 0),
        ),
    )

    assert LRPE.interpret_str(depth_two_chain) == 8

    with pytest.raises(MaterializationLimitError):
        LRPE.interpret_str(
            depth_two_chain,
            limits=MaterializationLimits(max_value=7),
        )


def test_lrpe_interpret_str_rejects_non_str_input() -> None:
    with pytest.raises(TypeError, match="STR input"):
        LRPE.interpret_str(object())  # type: ignore[arg-type]
