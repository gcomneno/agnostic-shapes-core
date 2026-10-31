# ASHES STE — EXP-001 / Structural C1

Status: frozen experimental protocol.
Authority: research only; no SHAPES semantic promotion.

## Question

Can a native C11 realization combine an explicitly identified
historical MOVE with a content update while preserving both
branch intentions and validating the resulting rooted tree?

This experiment does not establish general three-way merge.

## Controlled input

Historical vertex identifiers: r=0, p=1, q=2.

BASE:
    parent(r) = none
    parent(p) = r
    parent(q) = r
    content(p) = draft

LEFT:
    MOVE(p, q)
    content(p) = draft

RIGHT:
    unchanged incidence
    content(p) = final

Interpretation policy:
    relocation of p under q is permitted;
    content final is permitted in that position;
    both branch intentions must survive.

## Required result

MERGED:
    parent(r) = none
    parent(q) = r
    parent(p) = q
    content(p) = final

Historical identity:
    V_merged = V_base = {r,p,q}
    no vertex is deleted or newly created.

## Mandatory checks

C1_TREE:
    exactly one root, unique parents for non-root vertices,
    acyclic incidence and complete reachability.

C1_MOVE:
    p changes parent from r to q;
    all other original parent incidences remain unchanged.

C1_IDENTITY:
    historical vertex identities are preserved.
    This is not asserted to be a full TPI witness.

C1_CONTENT:
    the update draft -> final is retained.

C1_POLICY:
    interpretation explicitly accepts the merged state.

C1_INTENTIONS:
    neither branch intention is silently discarded.

## Negative controls

N1:
    moving the root must be rejected.

N2:
    moving a vertex under itself or one of its descendants
    must be rejected.

N3:
    a policy rejecting final content under q must not
    produce COMPATIBLE.

N4:
    missing or contradictory historical association must
    not be repaired by guessing from SHAPES equality.

## Falsification

FAIL if any mandatory check fails, if an invalid MOVE succeeds,
if a rejected merged state is accepted, or if historical identity
is inferred solely from structural equality.

Possible outcomes:
    PASS, PARTIAL, FAIL, INCONCLUSIVE.

## Boundaries

MOVE is a historical operation on a pointed realization, not
an intrinsic SHAPES elementary generator.

Content is interpretation-owned; the structural verifier treats
it as opaque data.

No generic diff, concurrent merge, CRDT, persistence,
runtime integration or performance claim is in scope.

References:
- docs/research/ste-m001-contract.md
- docs/reference/SPEC.md
- tools/research/tpi_algebra/move_002/FORMAL_NOTES.md
