# ASHES STE — EXP-001

Status: experimental C11 classifier.
Research contract: `docs/research/ste-m001-contract.md`.

## Purpose

Test whether explicitly supplied historical alternatives and
interpretation-owned decisions can be classified without deriving
persistent identity or domain semantics from SHAPES equality.

This is not yet a structural reconciliation engine.

## Current sources

- `ste.h`: experimental interface
- `ste.c`: alternative classification
- `test_ste.c`: frozen cases C1–C4 and two negative cases

## Observed execution

Native C11 build: PASS.

- C1 MOVE + content edit: COMPATIBLE
- C2 incompatible property updates: CONFLICT
- C3 consequential historical ambiguity: AMBIGUOUS
- C4 DELETE + content edit: CONFLICT
- Missing policy: UNSUPPORTED
- Unsupported policy decision: UNSUPPORTED

All six checks passed in the first recorded execution.

## Important limitations

The caller supplies the historical alternatives and identities.
The classifier does not discover or validate correspondences.

Subjects are opaque identifiers; the prototype does not prove that
they refer to valid SHAPES occurrences.

Pairwise policy acceptance is not a proof of global consistency.

No merged tree is constructed, validated or returned.

Individual branch validity, completeness of alternatives and
preservation of all branch intentions are caller assumptions,
not guarantees enforced by the current implementation.

No general three-way merge, concurrency, CRDT, production API,
performance or semantic correctness claim is established.

## Next research boundary

Qualify one concrete structural transformation and its resulting
state against the already frozen M001 contract.

Do not expand scope until this distinction is demonstrated.

No SHAPES SPEC or runtime modification is authorized by EXP-001.

## Structural C1 — observed result

Protocol: `C1_PROTOCOL.md`.
Implementation: `c1_realization.c`.
Tests: `test_c1.c`.

Native C11 behavioral execution: PASS (8/8).

- C1_MERGE: PASS
- N1_ROOT_MOVE: PASS
- N2_SELF_CYCLE: PASS
- N2_DESCENDANT_CYCLE: PASS
- N3_POLICY_REJECTION: PASS
- N4_HISTORICAL_IDENTITY: PASS
- RIGHT_UNDECLARED_MOVE: PASS
- MISSING_POLICY: PASS

The experiment constructs a merged pointed tree with the historical
vertex identifiers preserved, p moved under q, and p's content updated.

This establishes the behavior only for the bounded C1 implementation
and supplied historical associations. It does not establish a general
three-way merge algorithm, arbitrary identity reconciliation, or
global semantic consistency.

The original six classifier tests and this C1 realization are
separate experimental results.

## EXP-002 — Observed evidence

Protocol: `EXP002_PROTOCOL.md` (frozen before implementation).

Implementation:
- Historical IDs are resolved independently of local array indices.
- The unique root is identified through `NO_PARENT`.
- Parent incidences are compared through historical parent IDs.
- The C1 result retains LEFT's local ordering.

Observed strict C11 regression results:
- EXP-001 classifier: 6/6 PASS.
- EXP-001 structural C1: 8/8 PASS.
- EXP-002 permutation and negative controls: 12/12 PASS.
- Combined regression: 26/26 PASS.

The tested independent permutations preserve the same historical
identities, parent incidences, and contents. Invalid inputs and
unsupported edits are rejected within the bounded C1 contract.

Limitations:
- MAX_NODES remains 16.
- Historical identities must be supplied by the caller.
- No automatic identity discovery or general merge is established.
- No exhaustive proof for all permutations or input states is claimed.
- No SHAPES normative semantics or runtime changes are implied.

Outcome for the executed frozen checks: PASS.

## EXP-003 — Observed evidence

Protocol: `EXP003_PROTOCOL.md` (frozen before implementation).

Implementation:
- `c2_state.c` compares BASE, LEFT and RIGHT for one opaque
  property belonging to one explicitly identified subject.
- Actual changes are derived relative to BASE.
- Equal, one-sided and absent changes require no policy callback.
- Divergent updates are delegated to interpretation-owned policy.
- The result is a classification, not a merged property value.

Observed strict C11 execution:
- EXP-001 classifier: 6/6 PASS.
- EXP-001 structural C1: 8/8 PASS.
- EXP-002 permutation controls: 12/12 PASS.
- EXP-003 state-based C2: 10/10 PASS.
- Combined regression: 36/36 PASS across four executables.

For divergent changes, the supplied policy is called once.
Under rejection the result is CONFLICT; under acceptance it is
COMPATIBLE; absent or undecided policy yields UNSUPPORTED.
Invalid state input and mismatched historical IDs yield UNSUPPORTED.

Limitations:
- Exactly one scalar property and one historical subject.
- Historical identifiers and values are caller-supplied.
- Policy acceptance does not construct or validate a merge.
- No autonomous identity discovery, general structural merge,
  concurrency correctness or normative SHAPES behavior is claimed.

Outcome for the executed frozen checks: PASS.

## EXP-004 — Observed evidence

Protocol: `EXP004_PROTOCOL.md` (frozen before execution).

Implementation:
- Reuses the existing `ste_classify()` C11 classifier.
- Adds only `test_exp004.c` for controlled C3 fixtures.
- Historical association alternatives are supplied by the caller.
- No new classifier or historical identity inference was introduced.

Observed strict C11 execution:
- EXP-001 classifier: 6/6 PASS.
- EXP-001 structural C1: 8/8 PASS.
- EXP-002 permutation controls: 12/12 PASS.
- EXP-003 state-based C2: 10/10 PASS.
- EXP-004 C3 executable controls: 9/9 PASS.
- Combined regression: 45/45 PASS across five executables.

The classifier reports AMBIGUOUS when supplied admissible
alternatives imply materially different classifications.
Reversing their order does not affect that classification.

For the harmless-multiplicity fixture, identical material
outcomes are a caller assumption, not independently verified.

Research evidence limitation:
- C3_INCOMPLETE_EVIDENCE: INCONCLUSIVE.
- HISTORICAL_COMPLETENESS: NOT_ESTABLISHED.
- MATERIAL_OUTCOME_EQUIVALENCE: CALLER_ASSUMPTION.
- Candidate enumeration does not prove completeness.
- No autonomous reconstruction of historical associations.
- No general merge or normative SHAPES claim.

Outcome for the nine executable frozen controls: PASS.
Overall historical completeness remains INCONCLUSIVE.

## EXP-005 — Observed evidence

Protocol: `EXP005_PROTOCOL.md` (frozen before implementation).

Implementation:
- `c4_state.c` classifies one explicitly identified historical
  leaf across BASE, LEFT and RIGHT.
- Presence and opaque content changes are derived relative to BASE.
- A supplied absent state represents historical DELETE in this
  bounded model; absence is not inferred from SHAPES equality.
- DELETE versus content EDIT invokes interpretation-owned policy
  exactly once; other valid combinations require no policy call.
- Deleted-state content is ignored, including residual tombstone data.
- `test_c4_state.c` exercises the fourteen frozen C4 fixtures
  and an additional invalid-presence control.
- No merged value, tree or document is constructed.

Observed strict C11 execution:
- EXP-001 classifier: 6/6 PASS.
- EXP-001 structural C1: 8/8 PASS.
- EXP-002 permutation controls: 12/12 PASS.
- EXP-003 state-based C2: 10/10 PASS.
- EXP-004 C3 executable controls: 9/9 PASS.
- EXP-005 state-based C4: 14/14 PASS.
- Additional presence-domain validation: PASS.
- Combined regression: 59/59 PASS across six executables.

For competing historical DELETE and EDIT intentions:
- Restrictive policy: CONFLICT.
- Explicit deletion-wins authorization: COMPATIBLE.
- Missing or undecided policy: UNSUPPORTED.
- Reversing LEFT and RIGHT preserves the tested restrictive result.

One-sided changes, duplicate deletion, identical edits and
unchanged states are COMPATIBLE without a policy callback.
Invalid historical identities, missing states and invalid BASE
are UNSUPPORTED.

Research limitations:
- Exactly one historical leaf and one opaque content property.
- Historical identity and existence are caller-supplied.
- The verifier does not discover historical correspondences.
- Subtree DELETE, reinsertion, MOVE and general merge are excluded.
- COMPATIBLE under deletion-wins does not prove preservation
  of both original intentions or construct a reconciled result.
- Historical completeness remains NOT_ESTABLISHED.
- No general three-way merge, concurrency correctness, production
  API or normative SHAPES behavior is established.
- EXP-004 historical completeness remains INCONCLUSIVE.

Outcome for the fourteen frozen C4 controls: PASS.
Additional presence-domain control: PASS.
Combined C11 regression: 59/59 PASS.

## EXP-006 — Observed evidence

Protocol: `EXP006_PROTOCOL.md` (frozen before implementation).

Implementation:
- `two_moves.c` evaluates joint realizability of two historical
  MOVE intentions on bounded rooted trees.
- Reuses the existing C1 historical-tree representation and
  structural validators without modifying their sources.
- Historical identities are supplied explicitly by the caller.
- Parent incidences are compared by historical identity.
- A positive classification requires a concrete valid tree.
- Explicit SELECT_LEFT or SELECT_RIGHT policy authorizes
  dropping the opposite MOVE intention.
- Non-COMPATIBLE results leave the output state unchanged.
- `test_two_moves.c` executes ten frozen controls.

Observed strict C11 execution:
- EXP-001 classifier: 6/6 PASS.
- EXP-001 structural C1: 8/8 PASS.
- EXP-002 permutation controls: 12/12 PASS.
- EXP-003 state-based C2: 10/10 PASS.
- EXP-004 C3 executable controls: 9/9 PASS.
- EXP-005 state-based C4: 14/14 PASS.
- EXP-006 joint MOVE controls: 10/10 PASS.
- Additional EXP-005 presence-domain control: PASS.
- Combined regression: 69/69 PASS across seven executables.

Scientific observations:
- Individually valid MOVEs can produce a structural cycle
  when both historical parent-incidence requirements are imposed.
- PRESERVE_BOTH rejects the cyclic primary fixture: CONFLICT.
- Explicit selection of either individual valid branch yields
  COMPATIBLE with a verified structural witness.
- An acyclic two-MOVE combination yields COMPATIBLE with
  a verified witness preserving both intended incidences.
- Missing or undecided policy yields UNSUPPORTED.
- Invalid tree input, inconsistent historical identities
  and missing state input yield UNSUPPORTED.
- No silent selection occurs under PRESERVE_BOTH.

Research limitations:
- Exactly two declared historical MOVE intentions.
- Bounded rooted trees of at most sixteen vertices.
- Historical correspondence completeness is NOT_ESTABLISHED.
- These finite tests do not prove universal algorithmic soundness.
- No general three-way merge, arbitrary intention consistency,
  concurrency guarantee, production API or normative SHAPES
  semantic extension is established.
- EXP-004 historical completeness remains INCONCLUSIVE.

Outcome for ten frozen EXP-006 controls: PASS.
Combined C11 regression: 69/69 PASS.
Global merge correctness: NOT_ESTABLISHED.
