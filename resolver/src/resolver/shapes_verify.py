"""Path verification over intrinsic SHAPES edits.

This module is a Resolver satellite over SHAPES. It independently replays
proposed ADD/REMOVE steps against the evolving Shape state and optionally
checks minimality through the SHAPES-native structural distance layer.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from shapes import OccurrencePath, Shape, add, remove, validate

from .shapes_distance import DistanceError, structural_distance_shapes


class ShapesVerifyError(ValueError):
    """A deterministic SHAPES path-verification failure."""


class ShapesEditDirection(str, Enum):
    """Intrinsic SHAPES edit direction accepted by the verifier."""

    ADD = "ADD"
    REMOVE = "REMOVE"


@dataclass(frozen=True)
class ShapesVerifyStep:
    """One proposed intrinsic edit to replay independently."""

    direction: ShapesEditDirection
    target: OccurrencePath


@dataclass(frozen=True)
class ShapesStepFailure:
    """One well-formed proposed edit that could not be applied."""

    index: int
    step: ShapesVerifyStep
    before_shape: Shape
    reason: str


@dataclass(frozen=True)
class ShapesVerificationResult:
    """Outcome of independently replaying one proposed SHAPES path."""

    source: Shape
    target: Shape
    steps: tuple[ShapesVerifyStep, ...]
    final_shape: Shape
    valid: bool
    minimal: bool | None
    expected_length: int | None
    reason: str
    failed_step: ShapesStepFailure | None = None


def verify_shapes_path(
    source: Shape,
    target: Shape,
    steps: Iterable[ShapesVerifyStep],
    *,
    check_minimal: bool = True,
    max_depth: int = 30,
    max_nodes: int = 200,
    max_visited: int = 500_000,
    min_distance: int | None = None,
) -> ShapesVerificationResult:
    """Independently replay a proposed intrinsic SHAPES edit path."""

    _validate_min_distance(min_distance)

    try:
        validate(source)
        validate(target)
    except (TypeError, ValueError) as error:
        raise ShapesVerifyError(str(error)) from error

    normalized_steps = tuple(_validate_step(step) for step in steps)

    current = source

    for index, step in enumerate(normalized_steps):
        before = current

        try:
            if step.direction is ShapesEditDirection.ADD:
                current = add(current, step.target)
            else:
                current = remove(current, step.target)
        except ValueError as error:
            return ShapesVerificationResult(
                source=source,
                target=target,
                steps=normalized_steps,
                final_shape=before,
                valid=False,
                minimal=None,
                expected_length=None,
                reason="invalid-step",
                failed_step=ShapesStepFailure(
                    index=index,
                    step=step,
                    before_shape=before,
                    reason=_classify_edit_failure(step, str(error)),
                ),
            )

    if current != target:
        return ShapesVerificationResult(
            source=source,
            target=target,
            steps=normalized_steps,
            final_shape=current,
            valid=False,
            minimal=None,
            expected_length=None,
            reason="target-not-reached",
        )

    expected_length: int | None = None
    minimal: bool | None = None

    if check_minimal:
        if min_distance is None:
            try:
                expected_length = structural_distance_shapes(
                    source,
                    target,
                    max_depth=max_depth,
                    max_nodes=max_nodes,
                    max_visited=max_visited,
                )
            except DistanceError as error:
                raise ShapesVerifyError(str(error)) from error
        else:
            expected_length = min_distance

        minimal = len(normalized_steps) == expected_length
        reason = (
            "valid-and-minimal"
            if minimal
            else "valid-but-suboptimal"
        )
    else:
        reason = "valid"

    return ShapesVerificationResult(
        source=source,
        target=target,
        steps=normalized_steps,
        final_shape=current,
        valid=True,
        minimal=minimal,
        expected_length=expected_length,
        reason=reason,
    )


def _validate_step(step: object) -> ShapesVerifyStep:
    if not isinstance(step, ShapesVerifyStep):
        raise ShapesVerifyError("step must be ShapesVerifyStep")

    if not isinstance(step.direction, ShapesEditDirection):
        raise ShapesVerifyError("step direction must be ADD or REMOVE")

    target = step.target
    if not isinstance(target, tuple):
        raise ShapesVerifyError("step target must be an OccurrencePath tuple")

    if any(type(index) is not int or index < 0 for index in target):
        raise ShapesVerifyError(
            "step target must contain non-negative integer indices"
        )

    return step


def _validate_min_distance(min_distance: int | None) -> None:
    if min_distance is None:
        return
    if type(min_distance) is not int or min_distance < 0:
        raise ShapesVerifyError(
            "min_distance must be a non-negative integer"
        )


def _classify_edit_failure(
    step: ShapesVerifyStep,
    message: str,
) -> str:
    if (
        "occurrence path" in message
        or "out of range" in message
        or "crosses zero-child" in message
    ):
        return "invalid-occurrence-path"

    if step.direction is ShapesEditDirection.REMOVE:
        if not step.target:
            return "remove-root"
        if message == "REMOVE target must be zero-child":
            return "remove-non-leaf"

    return "invalid-edit"
