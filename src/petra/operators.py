"""Executable PETRA structural rewrites."""

from __future__ import annotations

from .addresses import (
    Address,
    AddressError,
    ResolvedAnchor,
    ResolvedSlot,
    ResolvedTerm,
    resolve_address,
)
from .intrinsic import intrinsic_add, intrinsic_remove
from .model import Container, Leaf, PetraShape, validate_shape
from .results import (
    AddressEffects,
    DefaultTarget,
    ExplicitTarget,
    FailedResult,
    InvocationTarget,
    Operator,
    OperatorResult,
    SuccessfulResult,
)


def _require_invocation_target(
    value: object,
) -> InvocationTarget:
    if not isinstance(
        value,
        (DefaultTarget, ExplicitTarget),
    ):
        raise TypeError(
            "invocation_target must be a normalized target"
        )

    return value


def _find_deepest_last_latent_slot(
    shape: PetraShape,
) -> Address | None:
    """Return the deepest-last latent slot in canonical preorder."""

    if isinstance(shape, Leaf):
        return None

    selected: Address | None = None
    selected_depth = -1

    def visit(
        current: Container,
        prefix: tuple[int, ...],
    ) -> None:
        nonlocal selected
        nonlocal selected_depth

        for index, current_term in enumerate(current.terms):
            owner_indices = (*prefix, index)
            depth = len(owner_indices)

            if isinstance(current_term.exponent, Leaf):
                if depth >= selected_depth:
                    selected = Address(
                        indices=owner_indices,
                        is_slot=True,
                    )
                    selected_depth = depth
            else:
                visit(
                    current_term.exponent,
                    owner_indices,
                )

    visit(shape, ())
    return selected


def _find_deepest_last_terminal_leaf(
    shape: PetraShape,
) -> Address | None:
    """Return the deepest-last eligible PRUNE target."""

    if isinstance(shape, Leaf):
        return None

    selected: Address | None = None
    selected_depth = -1

    def visit(
        current: Container,
        owner_prefix: tuple[int, ...],
    ) -> None:
        nonlocal selected
        nonlocal selected_depth

        for index, current_term in enumerate(current.terms):
            term_indices = (*owner_prefix, index)

            if isinstance(current_term.exponent, Leaf):
                is_nested = bool(owner_prefix)
                is_singleton_parent = len(current.terms) == 1

                if is_nested and is_singleton_parent:
                    depth = len(term_indices)

                    if depth >= selected_depth:
                        selected = Address(indices=term_indices)
                        selected_depth = depth
            else:
                visit(
                    current_term.exponent,
                    term_indices,
                )

    visit(shape, ())
    return selected


def _failure(
    *,
    operator: Operator,
    invocation_target: InvocationTarget,
    before_shape: PetraShape,
    reason: str,
) -> FailedResult:
    return FailedResult(
        operator=operator,
        invocation_target=invocation_target,
        before_shape=before_shape,
        reason=reason,
    )


def apply_sprout(
    shape: PetraShape,
    invocation_target: InvocationTarget,
) -> OperatorResult:
    """Apply one canonical PETRA width insertion."""

    validate_shape(shape)
    target = _require_invocation_target(invocation_target)

    if isinstance(target, DefaultTarget):
        target_address = Address()
        resolved = resolve_address(
            shape,
            target_address,
        )
    else:
        target_address = target.address

        try:
            resolved = resolve_address(
                shape,
                target_address,
            )
        except AddressError as error:
            return _failure(
                operator=Operator.SPROUT,
                invocation_target=target,
                before_shape=shape,
                reason=error.reason,
            )

    if isinstance(resolved, ResolvedAnchor):
        selected_shape = resolved.shape
        old_width = (
            0 if isinstance(selected_shape, Leaf)
            else len(selected_shape.terms)
        )
        after_shape = intrinsic_add(shape, ())
        witness_address = Address(indices=(old_width,))

    elif (
        isinstance(resolved, ResolvedTerm)
        and isinstance(resolved.term.exponent, Container)
    ):
        old_width = len(resolved.term.exponent.terms)
        after_shape = intrinsic_add(
            shape,
            resolved.address.indices,
        )
        witness_address = Address(
            indices=(
                *resolved.address.indices,
                old_width,
            )
        )

    else:
        return _failure(
            operator=Operator.SPROUT,
            invocation_target=target,
            before_shape=shape,
            reason="sprout-target-not-container",
        )

    return SuccessfulResult(
        operator=Operator.SPROUT,
        invocation_target=target,
        resolved_target=resolved,
        before_shape=shape,
        after_shape=after_shape,
        address_effects=AddressEffects(
            target_address=resolved.address,
            witness_address=witness_address,
        ),
    )

def apply_graft(
    shape: PetraShape,
    invocation_target: InvocationTarget,
) -> OperatorResult:
    """Apply one canonical PETRA depth insertion."""

    validate_shape(shape)
    target = _require_invocation_target(invocation_target)

    if isinstance(target, DefaultTarget):
        target_address = _find_deepest_last_latent_slot(shape)

        if target_address is None:
            return _failure(
                operator=Operator.GRAFT,
                invocation_target=target,
                before_shape=shape,
                reason="graft-no-eligible-latent-slot",
            )

        resolved = resolve_address(
            shape,
            target_address,
        )

    else:
        target_address = target.address

        try:
            resolved = resolve_address(
                shape,
                target_address,
            )
        except AddressError as error:
            return _failure(
                operator=Operator.GRAFT,
                invocation_target=target,
                before_shape=shape,
                reason=error.reason,
            )

        if not isinstance(resolved, ResolvedSlot):
            return _failure(
                operator=Operator.GRAFT,
                invocation_target=target,
                before_shape=shape,
                reason="graft-target-not-slot",
            )

        if isinstance(resolved.target, Container):
            return _failure(
                operator=Operator.GRAFT,
                invocation_target=target,
                before_shape=shape,
                reason="graft-slot-already-materialized",
            )

    if not isinstance(resolved, ResolvedSlot):
        raise AssertionError(
            "a selected GRAFT target must resolve to a slot"
        )

    if not isinstance(resolved.target, Leaf):
        raise AssertionError(
            "a selected GRAFT slot must be latent"
        )

    after_shape = intrinsic_add(
        shape,
        resolved.address.indices,
    )

    witness_address = Address(
        indices=(
            *resolved.address.indices,
            0,
        )
    )

    return SuccessfulResult(
        operator=Operator.GRAFT,
        invocation_target=target,
        resolved_target=resolved,
        before_shape=shape,
        after_shape=after_shape,
        address_effects=AddressEffects(
            target_address=resolved.address,
            witness_address=witness_address,
        ),
    )


def apply_prune(
    shape: PetraShape,
    invocation_target: InvocationTarget,
) -> OperatorResult:
    """Apply one canonical PETRA depth removal."""

    validate_shape(shape)
    target = _require_invocation_target(invocation_target)

    if isinstance(target, DefaultTarget):
        target_address = _find_deepest_last_terminal_leaf(shape)

        if target_address is None:
            return _failure(
                operator=Operator.PRUNE,
                invocation_target=target,
                before_shape=shape,
                reason="prune-no-eligible-terminal-leaf",
            )

        resolved = resolve_address(
            shape,
            target_address,
        )

    else:
        target_address = target.address

        try:
            resolved = resolve_address(
                shape,
                target_address,
            )
        except AddressError as error:
            return _failure(
                operator=Operator.PRUNE,
                invocation_target=target,
                before_shape=shape,
                reason=error.reason,
            )

        if not (
            isinstance(resolved, ResolvedTerm)
            and isinstance(resolved.term.exponent, Leaf)
        ):
            return _failure(
                operator=Operator.PRUNE,
                invocation_target=target,
                before_shape=shape,
                reason="prune-target-not-terminal-leaf",
            )

        parent_owner_indices = resolved.address.indices[:-1]

        if not parent_owner_indices:
            return _failure(
                operator=Operator.PRUNE,
                invocation_target=target,
                before_shape=shape,
                reason="prune-target-has-no-parent-relation",
            )

        parent_owner = resolve_address(
            shape,
            Address(indices=parent_owner_indices),
        )

        if not (
            isinstance(parent_owner, ResolvedTerm)
            and isinstance(parent_owner.term.exponent, Container)
        ):
            raise AssertionError(
                "a nested PRUNE target must have "
                "a materialized parent relation"
            )

        if len(parent_owner.term.exponent.terms) != 1:
            return _failure(
                operator=Operator.PRUNE,
                invocation_target=target,
                before_shape=shape,
                reason="prune-parent-not-singleton-exponent",
            )

    if not isinstance(resolved, ResolvedTerm):
        raise AssertionError(
            "a selected PRUNE target must resolve to a term"
        )

    if not isinstance(resolved.term.exponent, Leaf):
        raise AssertionError(
            "a selected PRUNE target must be a leaf term"
        )

    parent_owner_indices = resolved.address.indices[:-1]

    if not parent_owner_indices:
        raise AssertionError(
            "a selected PRUNE target must be nested"
        )

    after_shape = intrinsic_remove(
        shape,
        resolved.address.indices,
    )

    witness_address = Address(
        indices=parent_owner_indices,
        is_slot=True,
    )

    return SuccessfulResult(
        operator=Operator.PRUNE,
        invocation_target=target,
        resolved_target=resolved,
        before_shape=shape,
        after_shape=after_shape,
        address_effects=AddressEffects(
            target_address=resolved.address,
            witness_address=witness_address,
        ),
    )


def apply_shed(
    shape: PetraShape,
    invocation_target: InvocationTarget,
) -> OperatorResult:
    """Apply one canonical PETRA width removal."""

    validate_shape(shape)
    target = _require_invocation_target(invocation_target)

    if isinstance(target, DefaultTarget):
        if isinstance(shape, Leaf):
            return _failure(
                operator=Operator.SHED,
                invocation_target=target,
                before_shape=shape,
                reason="shed-no-eligible-top-level-leaf",
            )

        selected_index = next(
            (
                index
                for index in range(
                    len(shape.terms) - 1,
                    -1,
                    -1,
                )
                if isinstance(
                    shape.terms[index].exponent,
                    Leaf,
                )
            ),
            None,
        )

        if selected_index is None:
            return _failure(
                operator=Operator.SHED,
                invocation_target=target,
                before_shape=shape,
                reason="shed-no-eligible-top-level-leaf",
            )

        target_address = Address(
            indices=(selected_index,),
        )
        resolved = resolve_address(
            shape,
            target_address,
        )

    else:
        target_address = target.address

        try:
            resolved = resolve_address(
                shape,
                target_address,
            )
        except AddressError as error:
            return _failure(
                operator=Operator.SHED,
                invocation_target=target,
                before_shape=shape,
                reason=error.reason,
            )

        if not (
            isinstance(resolved, ResolvedTerm)
            and isinstance(resolved.term.exponent, Leaf)
        ):
            return _failure(
                operator=Operator.SHED,
                invocation_target=target,
                before_shape=shape,
                reason="shed-target-not-leaf",
            )

    if not isinstance(resolved, ResolvedTerm):
        raise AssertionError(
            "a selected SHED target must resolve to a term"
        )

    parent_indices = resolved.address.indices[:-1]

    if not parent_indices:
        if not isinstance(shape, Container):
            raise AssertionError(
                "a root SHED target requires a root container"
            )

        parent_width = len(shape.terms)
    else:
        parent_owner = resolve_address(
            shape,
            Address(indices=parent_indices),
        )

        if not (
            isinstance(parent_owner, ResolvedTerm)
            and isinstance(
                parent_owner.term.exponent,
                Container,
            )
        ):
            raise AssertionError(
                "a nested SHED target requires a container parent"
            )

        parent_width = len(
            parent_owner.term.exponent.terms
        )

    after_shape = intrinsic_remove(
        shape,
        resolved.address.indices,
    )

    if not parent_indices:
        witness_address = Address()
    elif parent_width == 1:
        witness_address = Address(
            indices=parent_indices,
            is_slot=True,
        )
    else:
        witness_address = Address(
            indices=parent_indices,
        )

    return SuccessfulResult(
        operator=Operator.SHED,
        invocation_target=target,
        resolved_target=resolved,
        before_shape=shape,
        after_shape=after_shape,
        address_effects=AddressEffects(
            target_address=resolved.address,
            witness_address=witness_address,
        ),
    )


__all__ = [
    "apply_graft",
    "apply_prune",
    "apply_shed",
    "apply_sprout",
]
