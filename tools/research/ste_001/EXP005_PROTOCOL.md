# ASHES STE — EXP-005: historical DELETE versus EDIT

Status: FROZEN PROTOCOL — IMPLEMENTATION PENDING
Research layer: nonnormative
Predecessors: EXP-001 through EXP-004
Language: C11

## Research question

Can a bounded state-based C4 verifier distinguish historical
deletion of a leaf from content modification of that same
historically identified leaf, and classify their interaction
according to an explicit interpretation-owned policy?

## Scope and ownership

BASE contains one explicitly identified historical leaf s.
Each branch supplies the historical identity, an existence
state, and an opaque content token when the leaf is present.

The existence state is part of the supplied historical
realization. It is not inferred from SHAPES structural
equality, TPI complements, or a missing array position.

Historical identity is supplied by the caller and must
match across BASE, LEFT, and RIGHT, including tombstones.

Only one leaf and one content property are in scope.
Subtree deletion, reinsertion, MOVE, identity discovery,
and general merge are excluded.

The verifier classifies intentions; it does not construct
or validate a merged document.

## Controlled primary fixture

Historical leaf: s, historical_id = 1.

BASE:  present, content = DRAFT
LEFT:  deleted, content not applicable
RIGHT: present, content = FINAL

The exclusive-intentions policy rejects discarding either
the historical DELETE or the RIGHT content update.

Expected: CONFLICT.

Under an explicitly supplied deletion-wins policy,
the same competing intentions may be classified COMPATIBLE,
without claiming both intentions survive unchanged.

## Frozen controls

C4_DELETE_EDIT_REJECT:
  BASE present; LEFT deleted; RIGHT edited.
  Exclusive-intentions policy rejects resolution.
  Expected: CONFLICT; one policy call.

C4_DELETE_EDIT_ALLOW:
  Same input, explicit deletion-wins authorization.
  Expected: COMPATIBLE; one policy call.

C4_REVERSED_BRANCHES:
  LEFT edited; RIGHT deleted.
  Exclusive-intentions policy rejects resolution.
  Expected: CONFLICT; one policy call.

C4_DELETE_ONLY:
  LEFT deleted; RIGHT unchanged.
  Expected: COMPATIBLE; no policy call.

C4_EDIT_ONLY:
  LEFT unchanged; RIGHT edited.
  Expected: COMPATIBLE; no policy call.

C4_BOTH_DELETE:
  Both branches delete the same historical leaf.
  Expected: COMPATIBLE; no policy call.

C4_BOTH_SAME_EDIT:
  Both branches apply the same content update.
  Expected: COMPATIBLE; no policy call.

C4_UNCHANGED:
  Both branches preserve BASE unchanged.
  Expected: COMPATIBLE; no policy call.

C4_MISSING_POLICY:
  DELETE and EDIT compete; no policy supplied.
  Expected: UNSUPPORTED.

C4_UNDECIDED_POLICY:
  DELETE and EDIT compete; policy cannot decide.
  Expected: UNSUPPORTED; one policy call.

C4_IDENTITY_MISMATCH:
  A branch supplies a different historical identity.
  Expected: UNSUPPORTED; no policy call.

C4_MISSING_STATE:
  Any required state pointer is absent.
  Expected: UNSUPPORTED; no policy call.

C4_INVALID_BASE:
  BASE is absent or already deleted.
  Expected: UNSUPPORTED.

C4_INVALID_TOMBSTONE:
  A deleted state has no canonical content; the verifier
  must ignore its content token, rather than interpret
  arbitrary residual bytes as an update.
  Expected: same result as the corresponding valid
  deletion fixture.

## Required behavioral contract

- Validate matching historical IDs before deriving edits.
- Derive existence and content changes relative to BASE.
- Treat a transition from present to absent as a declared
  historical DELETE within this controlled model.
- Never compare content values of deleted states.
- Consult interpretation policy only for competing
  historical DELETE and content EDIT intentions.
- Use STE_DELETE and STE_SET_PROPERTY when invoking
  the existing SteConflictPolicy callback.
- Do not silently select deletion-wins without policy.
- Do not construct a merged value or document.
- Keep COMPATIBLE, CONFLICT, AMBIGUOUS and UNSUPPORTED
  as exclusive classification results.

## Measurements

- Result classification for each frozen fixture.
- Number of interpretation-policy invocations.
- Consistency under LEFT/RIGHT branch reversal.
- Correct handling of deleted-state content tokens.
- Input and identity validation.
- Preservation of the existing 45 C11 checks.

## Falsification criteria

EXP-005 fails if:

1. DELETE versus EDIT is accepted without authorization.
2. Exclusive-intentions policy does not produce CONFLICT.
3. Explicit deletion-wins authorization is ignored.
4. One-sided, duplicate or absent changes yield conflicts.
5. Content associated with deletion is treated as an edit.
6. Missing policy is classified as a proven conflict.
7. Invalid identity or required input is accepted.
8. Branch reversal changes the restricted policy outcome.
9. Any previously passed STE regression fails.
10. SHAPES normative semantics or runtime are modified.

No criteria may be added retroactively to make a result pass.

## Outcome classes

PASS:
  All frozen executable criteria and regressions succeed.

FAIL:
  At least one frozen criterion is falsified.

INCONCLUSIVE:
  Required execution or evidence is incomplete.

UNSUPPORTED:
  An input exceeds this bounded historical contract.

## Implementation boundary

Prefer a small standalone C11 verifier and focused tests,
reusing SteResult, SteEdit and StePolicy from ste.h.

No changes to SHAPES, PETRA, TPI, ste.c, ste.h,
c1_realization.c, c2_state.c, or frozen prior protocols.

## Execution gates

1. Freeze this protocol.
2. Implement the bounded C4 verifier.
3. Run the frozen C4 behavioral controls.
4. Run all existing 45 C11 checks.
5. Record results and limitations.
6. Authorize commit and push separately.
