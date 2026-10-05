import pytest

from petra import (
    LRPE,
    MaterializationLimitError,
    MaterializationLimits,
    ReverseDomainError,
)
from shapes import Shape


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
