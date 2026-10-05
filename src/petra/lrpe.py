"""Maintained LRPE interpretation policy over SHAPES."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from shapes import Shape, validate


class ReverseDomainError(ValueError):
    """Raised when a positive integer is outside the LRPE reachable image."""


class MaterializationLimitError(RuntimeError):
    """Raised when an explicit runtime materialization limit is exceeded."""


@dataclass(frozen=True, slots=True)
class MaterializationLimits:
    """Optional runtime bounds that do not alter LRPE mathematical semantics."""

    max_exponent: int | None = None
    max_value: int | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("max_exponent", self.max_exponent),
            ("max_value", self.max_value),
        ):
            if value is not None and (type(value) is not int or value < 1):
                raise ValueError(f"{name} must be a positive integer or None")


@dataclass(frozen=True, slots=True)
class LRPEPolicy:
    """Local-Rank Paired-Exponent interpretation policy."""

    name: str = "lrpe"

    def interpret(
        self,
        shape: Shape,
        *,
        limits: MaterializationLimits | None = None,
    ) -> int:
        """Interpret one SHAPES form under LRPE."""

        validate(shape)
        return _interpret(shape, limits)

    def reverse(self, value: int) -> Shape:
        """Reverse one positive integer when it belongs to the LRPE image."""

        if type(value) is not int:
            raise TypeError("LRPE reverse input must be an integer")

        if value < 1:
            raise ValueError("LRPE reverse input must be positive")

        return _reverse(value)


LRPE = LRPEPolicy()


def _interpret(
    shape: Shape,
    limits: MaterializationLimits | None,
) -> int:
    """Evaluate LRPE iteratively so Python call-stack depth is not semantic."""

    values: dict[Shape, int] = {}
    pending: list[tuple[Shape, bool]] = [(shape, False)]

    while pending:
        current, expanded = pending.pop()

        if current in values:
            continue

        classes = _child_classes(current)

        if not expanded:
            pending.append((current, True))

            for child, _multiplicity in reversed(classes):
                if child not in values:
                    pending.append((child, False))

            continue

        if not classes:
            values[current] = 1
            continue

        result = 1

        for rank, (child, multiplicity) in enumerate(classes, start=1):
            child_value = values[child]
            exponent = _pair(multiplicity, child_value)

            _check_exponent_limit(exponent, limits)

            prime = _nth_prime(rank)

            if limits is not None and limits.max_value is not None:
                factor_limit = limits.max_value // result

                if _power_exceeds(prime, exponent, factor_limit):
                    raise MaterializationLimitError(
                        "LRPE value exceeds configured max_value"
                    )

            result *= prime**exponent

        values[current] = result

    return values[shape]


def _child_classes(shape: Shape) -> list[tuple[Shape, int]]:
    """Return distinct child classes in SHAPES canonical structural order."""

    classes: list[tuple[Shape, int]] = []

    for child in shape.children:
        if classes and classes[-1][0] == child:
            previous_child, multiplicity = classes[-1]
            classes[-1] = (previous_child, multiplicity + 1)
        else:
            classes.append((child, 1))

    return classes


def _reverse(value: int) -> Shape:
    if value == 1:
        return Shape()

    factors = _factorize(value)
    expected_primes = tuple(_nth_prime(rank) for rank in range(1, len(factors) + 1))
    actual_primes = tuple(prime for prime, _ in factors)

    if actual_primes != expected_primes:
        raise ReverseDomainError(
            "LRPE value does not have contiguous initial prime support"
        )

    decoded: list[tuple[Shape, int]] = []

    for _prime, exponent in factors:
        multiplicity, child_value = _unpair(exponent)

        try:
            child = _reverse(child_value)
        except ReverseDomainError as exc:
            raise ReverseDomainError(
                "LRPE exponent contains a child value outside the reachable image"
            ) from exc

        decoded.append((child, multiplicity))

    children = [child for child, _ in decoded]

    if len(set(children)) != len(children):
        raise ReverseDomainError(
            "LRPE factors decode to duplicate structural child classes"
        )

    keys = [_structural_key(child) for child in children]

    if keys != sorted(keys):
        raise ReverseDomainError(
            "LRPE decoded child classes violate local structural rank"
        )

    occurrences: list[Shape] = []

    for child, multiplicity in decoded:
        occurrences.extend([child] * multiplicity)

    return Shape(children=tuple(occurrences))


def _pair(multiplicity: int, child_value: int) -> int:
    return (1 << (multiplicity - 1)) * (2 * child_value - 1)


def _unpair(exponent: int) -> tuple[int, int]:
    power_of_two = 0
    odd_part = exponent

    while odd_part % 2 == 0:
        power_of_two += 1
        odd_part //= 2

    multiplicity = power_of_two + 1
    child_value = (odd_part + 1) // 2

    return multiplicity, child_value


def _structural_key(shape: Shape) -> str:
    return "(" + "".join(_structural_key(child) for child in shape.children) + ")"


@cache
def _nth_prime(index: int) -> int:
    if index < 1:
        raise ValueError("prime index must be positive")

    found = 0
    candidate = 1

    while found < index:
        candidate += 1

        if _is_prime(candidate):
            found += 1

    return candidate


def _is_prime(value: int) -> bool:
    if value < 2:
        return False

    divisor = 2

    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1

    return True


def _factorize(value: int) -> list[tuple[int, int]]:
    remainder = value
    factors: list[tuple[int, int]] = []
    divisor = 2

    while divisor * divisor <= remainder:
        if remainder % divisor:
            divisor = 3 if divisor == 2 else divisor + 2
            continue

        exponent = 0

        while remainder % divisor == 0:
            remainder //= divisor
            exponent += 1

        factors.append((divisor, exponent))
        divisor = 3 if divisor == 2 else divisor + 2

    if remainder > 1:
        factors.append((remainder, 1))

    return factors


def _check_exponent_limit(
    exponent: int,
    limits: MaterializationLimits | None,
) -> None:
    if (
        limits is not None
        and limits.max_exponent is not None
        and exponent > limits.max_exponent
    ):
        raise MaterializationLimitError(
            "LRPE exponent exceeds configured max_exponent"
        )


def _power_exceeds(base: int, exponent: int, limit: int) -> bool:
    """Return whether ``base ** exponent`` exceeds ``limit`` without building it."""

    if limit < 1:
        return True

    result = 1
    factor = base
    remaining = exponent

    while remaining:
        if remaining & 1:
            if factor > limit // result:
                return True
            result *= factor

        remaining >>= 1

        if remaining:
            if factor > limit // factor:
                factor = limit + 1
            else:
                factor *= factor

    return False
