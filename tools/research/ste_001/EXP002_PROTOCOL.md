# ASHES STE — EXP-002: historical identity under local permutations

Status: FROZEN PROTOCOL — IMPLEMENTATION PENDING
Research layer: nonnormative
Predecessor: EXP-001 / C1
Language: C11

## Research question

Can the bounded C1 reconciler preserve historical identities,
parent incidences, and content changes when BASE, LEFT, and RIGHT
use independent local node-index arrangements?

## Scope

Only the existing C1 scenario is in scope:

- LEFT changes exactly one historical parent incidence.
- RIGHT changes exactly one historical content value.
- Historical identifiers are explicitly supplied by the caller.
- All three states contain the same finite set of historical IDs.
- Each state uses local indices for its parent references.
- MAX_NODES remains 16.
- The resulting state may retain LEFT's local node arrangement.

No historical identity discovery, general merge, concurrent editing,
persistent storage, or SHAPES semantic extension is claimed.

## Controlled inputs

Baseline:

- Historical root r = 0, initially parentless.
- Historical node p = 1, initially under r, content DRAFT.
- Historical node q = 2, initially under r.
- LEFT moves p under q.
- RIGHT changes p's content from DRAFT to FINAL.
- Policy accepts the resulting valid tree.

Representation variation:

- Independently permute node-array positions in BASE, LEFT,
  and RIGHT.
- Recalculate each state's local parent indices consistently.
- Include an arrangement with the historical root outside index 0.
- Keep historical IDs, incidences, and contents otherwise unchanged.

Negative controls:

- Duplicate historical ID.
- Missing or substituted historical ID.
- Invalid local parent index.
- Self-cycle or descendant-cycle.
- Illegal move of the historical root.
- Policy rejecting the combined result.
- Missing policy.
- An undeclared LEFT content edit or RIGHT incidence change.

## Measurements

- C1 return classification.
- Historical ID set in the output.
- Output root identity.
- Parent identity of every historical node, resolved through
  local parent indices.
- Content of every historical node.
- Rejection of invalid and unsupported inputs.
- Preservation of EXP-001 C1 and classifier regressions.

Compare outputs by historical identities, parent identities,
and contents, never by array position.

## Falsification criteria

EXP-002 fails if:

1. A representation-only permutation changes C1's acceptance.
2. Equivalent representations produce different historical
   parent incidences or content values.
3. A malformed or mismatched historical identity set is accepted.
4. An invalid tree or forbidden C1 edit is accepted.
5. An existing EXP-001 regression fails.

No outcome may be reclassified after observing test results
without explicitly revising and versioning this protocol.

## Outcome classes

PASS:
  All frozen behavioral and regression criteria hold.

FAIL:
  A frozen criterion is falsified.

INCONCLUSIVE:
  Evidence is incomplete or a required check cannot run.

UNSUPPORTED:
  The requested scenario exceeds the bounded C1 contract.

## Implementation boundary

Candidate approach:

- Resolve supplied historical IDs to local indices via bounded
  linear search.
- Detect the unique root through NO_PARENT.
- Compare parent identities, not raw parent indices.
- Apply RIGHT's content update to the corresponding node in
  the LEFT-ordered output.
- Make policy tests independent of local node positions.

No hash table, allocation framework, public API promotion,
or modification to docs/reference/SPEC.md is authorized.

## Execution gates

1. Protocol freeze and review.
2. Focused C11 behavioral implementation.
3. EXP-001 regressions plus EXP-002 positive and negative tests.
4. Document actual results, including negative findings.
5. Separate authorization for commit and push.
