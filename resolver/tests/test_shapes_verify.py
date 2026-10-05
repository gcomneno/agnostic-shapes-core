"""Tests for SHAPES-native path verification."""

from __future__ import annotations

import pytest
from shapes import Shape, add

from resolver.shapes_distance import DistanceError
from resolver.shapes_verify import (
    ShapesEditDirection,
    ShapesVerificationResult,
    ShapesVerifyError,
    ShapesVerifyStep,
    verify_shapes_path,
)


def _unary(depth: int) -> Shape:
    shape = Shape()
    for _ in range(depth):
        shape = Shape(children=(shape,))
    return shape


def test_empty_identity_path_is_valid_and_minimal() -> None:
    shape = Shape(children=(Shape(),))

    result = verify_shapes_path(shape, shape, ())

    assert result.valid is True
    assert result.minimal is True
    assert result.expected_length == 0
    assert result.reason == "valid-and-minimal"
    assert result.final_shape == shape


def test_one_valid_add() -> None:
    source = Shape()
    target = add(source, ())

    result = verify_shapes_path(
        source,
        target,
        (
            ShapesVerifyStep(
                ShapesEditDirection.ADD,
                (),
            ),
        ),
    )

    assert result.valid is True
    assert result.minimal is True
    assert result.final_shape == target


def test_one_valid_remove() -> None:
    source = Shape(children=(Shape(),))
    target = Shape()

    result = verify_shapes_path(
        source,
        target,
        (
            ShapesVerifyStep(
                ShapesEditDirection.REMOVE,
                (0,),
            ),
        ),
    )

    assert result.valid is True
    assert result.minimal is True


def test_invalid_add_path_returns_invalid_step() -> None:
    result = verify_shapes_path(
        Shape(),
        Shape(),
        (
            ShapesVerifyStep(
                ShapesEditDirection.ADD,
                (0,),
            ),
        ),
    )

    assert result.valid is False
    assert result.reason == "invalid-step"
    assert result.failed_step is not None
    assert result.failed_step.reason == "invalid-occurrence-path"


def test_remove_invalid_path_is_not_misclassified_as_non_leaf() -> None:
    result = verify_shapes_path(
        Shape(),
        Shape(),
        (
            ShapesVerifyStep(
                ShapesEditDirection.REMOVE,
                (0,),
            ),
        ),
    )

    assert result.valid is False
    assert result.reason == "invalid-step"
    assert result.failed_step is not None
    assert result.failed_step.reason == "invalid-occurrence-path"


def test_remove_root_returns_invalid_step() -> None:
    result = verify_shapes_path(
        Shape(),
        Shape(),
        (
            ShapesVerifyStep(
                ShapesEditDirection.REMOVE,
                (),
            ),
        ),
    )

    assert result.valid is False
    assert result.failed_step is not None
    assert result.failed_step.reason == "remove-root"


def test_remove_non_leaf_returns_invalid_step() -> None:
    source = _unary(2)

    result = verify_shapes_path(
        source,
        source,
        (
            ShapesVerifyStep(
                ShapesEditDirection.REMOVE,
                (0,),
            ),
        ),
    )

    assert result.valid is False
    assert result.failed_step is not None
    assert result.failed_step.reason == "remove-non-leaf"


def test_target_not_reached() -> None:
    source = Shape()
    target = _unary(2)

    result = verify_shapes_path(
        source,
        target,
        (
            ShapesVerifyStep(
                ShapesEditDirection.ADD,
                (),
            ),
        ),
    )

    assert result.valid is False
    assert result.reason == "target-not-reached"
    assert result.failed_step is None


def test_valid_two_step_path() -> None:
    source = Shape()
    target = _unary(2)

    result = verify_shapes_path(
        source,
        target,
        (
            ShapesVerifyStep(ShapesEditDirection.ADD, ()),
            ShapesVerifyStep(ShapesEditDirection.ADD, (0,)),
        ),
    )

    assert result.valid is True
    assert result.minimal is True
    assert result.expected_length == 2


def test_paths_are_interpreted_against_evolving_state() -> None:
    source = Shape(
        children=(
            _unary(2),
            Shape(children=(Shape(), Shape())),
        )
    )

    after_remove = source
    after_remove = Shape(
        children=(
            Shape(children=(Shape(),)),
            Shape(children=(Shape(), Shape())),
        )
    )
    target = add(after_remove, (1,))

    result = verify_shapes_path(
        source,
        target,
        (
            ShapesVerifyStep(
                ShapesEditDirection.REMOVE,
                (0, 0, 0),
            ),
            ShapesVerifyStep(
                ShapesEditDirection.ADD,
                (1,),
            ),
        ),
        check_minimal=False,
    )

    assert result.valid is True
    assert result.final_shape == target


def test_valid_but_suboptimal_path() -> None:
    source = Shape()
    target = Shape(children=(Shape(),))

    result = verify_shapes_path(
        source,
        target,
        (
            ShapesVerifyStep(ShapesEditDirection.ADD, ()),
            ShapesVerifyStep(ShapesEditDirection.ADD, (0,)),
            ShapesVerifyStep(ShapesEditDirection.REMOVE, (0, 0)),
        ),
    )

    assert result.valid is True
    assert result.minimal is False
    assert result.expected_length == 1
    assert result.reason == "valid-but-suboptimal"


def test_minimality_can_be_skipped() -> None:
    shape = Shape()

    result = verify_shapes_path(
        shape,
        shape,
        (),
        check_minimal=False,
    )

    assert result.valid is True
    assert result.minimal is None
    assert result.expected_length is None
    assert result.reason == "valid"


def test_precomputed_min_distance_is_used() -> None:
    source = Shape()
    target = Shape(children=(Shape(),))

    result = verify_shapes_path(
        source,
        target,
        (
            ShapesVerifyStep(ShapesEditDirection.ADD, ()),
        ),
        min_distance=1,
        max_depth=0,
    )

    assert result.valid is True
    assert result.minimal is True
    assert result.expected_length == 1


@pytest.mark.parametrize("value", [-1, True, 1.5, "1"])
def test_invalid_min_distance_is_rejected(value: object) -> None:
    with pytest.raises(
        ShapesVerifyError,
        match="min_distance must be a non-negative integer",
    ):
        verify_shapes_path(
            Shape(),
            Shape(),
            (),
            min_distance=value,  # type: ignore[arg-type]
        )


def test_malformed_step_is_rejected() -> None:
    with pytest.raises(
        ShapesVerifyError,
        match="step must be ShapesVerifyStep",
    ):
        verify_shapes_path(
            Shape(),
            Shape(),
            (object(),),  # type: ignore[arg-type]
        )


def test_invalid_step_target_is_rejected() -> None:
    step = ShapesVerifyStep(
        ShapesEditDirection.ADD,
        (True,),  # type: ignore[arg-type]
    )

    with pytest.raises(
        ShapesVerifyError,
        match="non-negative integer indices",
    ):
        verify_shapes_path(Shape(), Shape(), (step,))


def test_distance_failure_translates_to_verify_error() -> None:
    source = Shape()
    target = _unary(2)

    with pytest.raises(
        ShapesVerifyError,
        match="no path found",
    ) as excinfo:
        verify_shapes_path(
            source,
            target,
            (
                ShapesVerifyStep(ShapesEditDirection.ADD, ()),
                ShapesVerifyStep(ShapesEditDirection.ADD, (0,)),
            ),
            max_depth=1,
        )

    assert isinstance(excinfo.value.__cause__, DistanceError)


def test_result_type_is_shapes_specific() -> None:
    result = verify_shapes_path(
        Shape(),
        Shape(),
        (),
        check_minimal=False,
    )

    assert isinstance(result, ShapesVerificationResult)
