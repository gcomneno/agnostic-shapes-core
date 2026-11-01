# ASHES STE — EXP-006: Global Structural Soundness

Status: FROZEN PROTOCOL — IMPLEMENTATION PENDING
Authority: nonnormative STE research
Predecessors: EXP-001 through EXP-005
Language: C11

## Research question

Can a bounded reconciler determine whether two historical
MOVE intentions are jointly realizable as a valid rooted tree,
distinguishing structural impossibility from explicitly
authorized loss of an intention?

## Hypothesis

Individual validity of BASE -> LEFT and BASE -> RIGHT
does not imply joint realizability of the two intentions.

A positive reconciliation requires a concrete, valid
structural witness satisfying all intentions retained
under the declared policy.

## Controlled model

- Finite rooted tree with at most 16 historical vertices.
- BASE, LEFT and RIGHT contain the same historical IDs.
- Historical IDs are caller-supplied and unique per state.
- Each branch changes exactly one non-root parent incidence.
- No content changes, deletion, insertion or reinsertion.
- No inference of historical identity from SHAPES equality.
- Parent comparisons use historical IDs, not local indices.
- Each input state must be a valid rooted tree.
- Policy decisions are interpretation-owned.
- No general merge, TPI modification or SHAPES promotion.

## Primary counterexample

Historical IDs: r=0, p=1, q=2.

BASE:
    parent(r) = none
    parent(p) = r
    parent(q) = r

LEFT:
    MOVE(p, q)
    parent(p) = q
    parent(q) = r

RIGHT:
    MOVE(q, p)
    parent(q) = p
    parent(p) = r

BASE, LEFT and RIGHT are individually valid.

Preserving both MOVE intentions would require:

    parent(p) = q
    parent(q) = p

This introduces a directed cycle and admits no valid
rooted-tree realization.

## Policy interpretation

PRESERVE_BOTH:
    Both MOVE intentions are mandatory.
    No unilateral selection is authorized.

SELECT_LEFT:
    Explicitly authorizes dropping the RIGHT MOVE.
    Retain and validate the LEFT realization.

SELECT_RIGHT:
    Explicitly authorizes dropping the LEFT MOVE.
    Retain and validate the RIGHT realization.

UNDECIDED:
    No selection or preservation rule is established.

The selection policies represent authorized losses,
not simultaneous preservation of both intentions.

An absent or undecided policy is not evidence that
all supported reconciliation alternatives conflict.

## Frozen executable controls

G1_CYCLIC_BOTH:
    Primary counterexample, PRESERVE_BOTH.
    Expected: CONFLICT.
    No reconciled tree is accepted.

G2_CYCLIC_SELECT_LEFT:
    Primary counterexample, SELECT_LEFT.
    Expected: COMPATIBLE.
    Valid witness equals the LEFT historical incidence.

G3_CYCLIC_SELECT_RIGHT:
    Primary counterexample, SELECT_RIGHT.
    Expected: COMPATIBLE.
    Valid witness equals the RIGHT historical incidence.

G4_CYCLIC_NO_POLICY:
    Primary counterexample, policy absent.
    Expected: UNSUPPORTED.

G5_CYCLIC_UNDECIDED:
    Primary counterexample, policy undecided.
    Expected: UNSUPPORTED.

G6_ACYCLIC_BOTH:
    BASE contains root r and siblings p, q, t.
    LEFT moves p under q.
    RIGHT moves t under q.
    The combined parent incidences form a valid tree.
    PRESERVE_BOTH must accept the concrete combined tree.
    Expected: COMPATIBLE.

G7_INVALID_BRANCH:
    At least one supplied branch is cyclic.
    Expected: UNSUPPORTED or INVALID_INPUT in the
    local verifier result domain, but never COMPATIBLE.
    The chosen representation must be fixed before tests.

G8_IDENTITY_MISMATCH:
    Historical ID sets differ across supplied states.
    Expected: UNSUPPORTED or INVALID_INPUT in the
    local verifier result domain, but never COMPATIBLE.
    The chosen representation must be fixed before tests.

G9_MISSING_INPUT:
    A required state pointer is absent.
    Expected: UNSUPPORTED.

G10_NO_SILENT_SELECTION:
    The cyclic primary fixture must never select
    LEFT or RIGHT under PRESERVE_BOTH.

## Measurements

- Validity of each supplied tree.
- Correct historical parent-incidence comparison.
- Detection of joint cyclic inconsistency.
- Construction and validation of positive witnesses.
- Preservation or authorized loss of branch intentions.
- Treatment of absent or undecided policy.
- Rejection of malformed historical inputs.
- Preservation of the existing 59 C11 checks.

## Falsification criteria

EXP-006 fails if:

1. An invalid input tree is accepted as valid.
2. Historical identity is inferred from array positions.
3. The cyclic combined MOVE is accepted under PRESERVE_BOTH.
4. A valid acyclic combined MOVE is rejected without cause.
5. COMPATIBLE is returned without a valid output witness.
6. A branch intention is discarded without authorization.
7. An explicitly selected valid realization is rejected.
8. Missing policy silently selects an intention.
9. A malformed historical identity set is accepted.
10. Existing STE regressions fail.
11. SHAPES normative semantics or runtime are modified.

No criteria may be changed retroactively to obtain PASS.

## Outcome classes

PASS:
    All frozen controls and regressions succeed.

FAIL:
    One or more frozen criteria are falsified.

INCONCLUSIVE:
    Evidence or required execution is incomplete.

UNSUPPORTED:
    Input or policy exceeds the bounded model.

## Scientific limitations

This experiment assumes the historical associations
are correctly supplied and does not prove completeness
of possible associations.

Joint realizability is tested only for two declared
MOVE intentions on bounded rooted trees.

A positive result does not establish a general merge,
semantic consistency across arbitrary properties,
concurrent reconciliation or a production API.

## Execution sequence

1. Freeze protocol before implementation.
2. Fix any representation choices left open above.
3. Implement a minimal standalone C11 verifier.
4. Run the frozen focused controls.
5. Run the previous 59 C11 checks.
6. Record positive, negative and inconclusive evidence.
7. Authorize commit and push separately.

No changes to ste.c, ste.h, existing frozen protocols,
SHAPES SPEC, SHAPES runtime or TPI are authorized.
