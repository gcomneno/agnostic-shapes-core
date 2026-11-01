# ASHES STE — EXP-003: state-based C2 conflict detection

Status: FROZEN PROTOCOL — IMPLEMENTATION PENDING
Research layer: nonnormative
Predecessors: EXP-001, EXP-002
Language: C11

## Research question

Can a bounded state-based C2 verifier derive actual changes
from BASE, LEFT and RIGHT, and classify divergent updates to
one historically identified property according to an explicit
interpretation-owned policy?

## Scope and ownership

Each subject has one scalar property k with an opaque value.
The subject's historical ID is explicitly supplied by the caller.

This experiment does not introduce a general property model,
discover historical identity, modify SHAPES semantics, or
establish a general structural merge.

The state-based verifier is separate from the existing
EXP-001 classifier and EXP-002 structural C1 reconciler.

## Controlled input

Historical subject p has ID 1.

Primary C2 fixture:

BASE:  k(p) = 0
LEFT:  k(p) = 1
RIGHT: k(p) = 2

Both branches require preserving their respective update.
The declared exclusive-update policy forbids automatically
selecting, combining or discarding either different value.

Expected result: CONFLICT.

The property values are opaque tokens; their meaning belongs
to the interpretation, not to SHAPES.

## Frozen positive and negative controls

C2_DIVERGENT:
  BASE=0, LEFT=1, RIGHT=2.
  Exclusive-update policy rejects combined intentions.
  Expected: CONFLICT.

SAME_UPDATE:
  BASE=0, LEFT=1, RIGHT=1.
  Both branches express the same resulting value.
  Expected: COMPATIBLE.

LEFT_ONLY:
  BASE=0, LEFT=1, RIGHT=0.
  Exactly one branch changes the property.
  Expected: COMPATIBLE.

RIGHT_ONLY:
  BASE=0, LEFT=0, RIGHT=2.
  Exactly one branch changes the property.
  Expected: COMPATIBLE.

UNCHANGED:
  BASE=0, LEFT=0, RIGHT=0.
  Neither branch changes the property.
  Expected: COMPATIBLE.

POLICY_ALLOW:
  BASE=0, LEFT=1, RIGHT=2.
  An explicitly supplied resolution policy authorizes
  the coexistence or resolution of the two intentions.
  Expected: COMPATIBLE under that policy only.

POLICY_UNSUPPORTED:
  BASE=0, LEFT=1, RIGHT=2.
  Policy cannot decide.
  Expected: UNSUPPORTED.

MISSING_POLICY:
  BASE=0, LEFT=1, RIGHT=2.
  No interpretation policy is supplied.
  Expected: UNSUPPORTED.

IDENTITY_MISMATCH:
  BASE, LEFT and RIGHT do not identify the same
  historical subject.
  Expected: UNSUPPORTED.

INVALID_INPUT:
  Missing required state input.
  Expected: UNSUPPORTED.

## Required behavioral contract

The verifier must:

- compare the explicitly supplied historical IDs;
- derive changes from the three input values;
- avoid fabricating edits for unchanged branches;
- detect equal updates without treating them as divergent;
- consult interpretation policy for divergent updates;
- never infer semantic conflict from SHAPES structure alone;
- return mutually exclusive result classes;
- avoid selecting or constructing an output value unless
  the declared experimental contract supports doing so.

For POLICY_ALLOW, COMPATIBLE is only a classification of
policy-authorized intentions. The experiment does not claim
to construct or validate a merged output.

A missing policy does not prove CONFLICT.

## Measurements

- Classification for every frozen fixture.
- Detection of actual changes against BASE.
- Historical ID validation.
- Policy invocation only where both branches have
  materially divergent updates requiring a decision.
- Preservation of EXP-001 and EXP-002 regressions.

## Falsification criteria

EXP-003 fails if:

1. C2_DIVERGENT is accepted under exclusive-update policy.
2. Equal updates or one-sided updates become conflicts.
3. Unchanged inputs are represented as competing changes.
4. A divergent update is accepted without an explicit
   applicable policy decision.
5. Invalid or mismatched historical inputs are accepted.
6. Output depends on arbitrary local array positions.
7. An existing EXP-001 or EXP-002 regression fails.
8. Any implementation changes normative SHAPES semantics.

No criteria may be retroactively changed to make results pass.

## Outcome classes

PASS:
  All frozen checks and applicable regressions succeed.

FAIL:
  At least one frozen criterion is falsified.

INCONCLUSIVE:
  Required evidence or execution is incomplete.

UNSUPPORTED:
  An input scenario lies outside this bounded contract.

## Implementation boundary

Use a small standalone C11 research verifier and tests.
Reuse existing SteResult classes where appropriate.

No changes to:

- docs/reference/SPEC.md
- SHAPES runtime
- tools/research/ste_001/ste.c
- tools/research/ste_001/ste.h
- tools/research/ste_001/c1_realization.c
- existing EXP-001 and EXP-002 test fixtures
- unrelated SDO/TPI research

## Execution gates

1. Freeze and review this protocol.
2. Implement bounded state comparison.
3. Execute focused C11 controls.
4. Execute existing 26-test regression.
5. Record actual evidence and limitations.
6. Authorize commit and push separately.
