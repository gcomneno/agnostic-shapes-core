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
