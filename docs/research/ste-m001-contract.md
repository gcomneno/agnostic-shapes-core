# ASHES — Structural Transformation Engine, Mission 001

Status: approved research direction; initial contract, not an implementation.
Authority: research only. No SHAPES SPEC or runtime promotion.

## 1. Objective

Investigate a domain-agnostic transformation layer over SHAPES,
reusing TPI correspondences where their structural contracts apply.

The first evaluation domain is three-way reconciliation of a small
hierarchical document. Domain semantics remain outside SHAPES and STE.

No general-purpose merge algorithm is claimed at this stage.

## 2. Existing foundations

SHAPES provides canonical unordered rooted-tree forms and intrinsic
ADD/REMOVE relations.

TPI provides rooted ancestor-closed partial correspondences preserving
direct incidence, as well as composition and endpoint complements.

Research prototypes already represent structural deltas and their
composition. They are evidence, not public stable STE dependencies.

MOVE-002 distinguishes historical identity from TPI correspondence.
A concrete MOVE may preserve all vertices while changing incidence,
and may have canonically equal source and target forms.

Endpoint-completeness of local witnessed-edit path congruence does not
preserve historical survivor correspondences.

## 3. Information levels

FORM:
    structural equality modulo rooted-tree isomorphism

CORRESPONDENCE:
    explicit partial mapping between source and target occurrences,
    subject to the selected structural contract

HISTORY:
    optional persistent identities and operation provenance,
    supplied by an external history model or interpretation

SEMANTICS:
    labels, content, ordering, types, validity constraints and
    domain-specific conflict policy, supplied by the interpretation

No information level may silently substitute for another.

## 4. Proposed transformation contract

A transformation candidate records:

- source and target structural states;
- a TPI correspondence with a declared validity discipline;
- TPI complements relative to that selected correspondence;
- separately supplied historical identities, births, deaths and MOVE
  provenance when historical claims are required;
- branch intentions and their required preservation conditions;
- a declared interpretation policy for semantic validation.

TPI complements are not automatically historical births or deaths.

A genuine historical MOVE may preserve every vertex while changing
parent incidence. For a nontrivial MOVE of subtree D, the largest
TPI witness constrained to historical identity is id_(V minus D).
This is not a bound on alternative endpoint TPI witnesses.

A minimal enriched state consists of concrete occurrence-local
annotations plus a forgetful projection to the underlying SHAPES
form. The projection forgets labels, order and persistent identity.

Neither structural equality nor a TPI witness establishes historical
identity or semantic validity.

The interpretation owns content, types, ordering and domain constraints.
When an enriched model cannot be projected faithfully to the declared
structural contract, its use is outside the first prototype.

## 5. Reconciliation contract and exclusive results

Given BASE, LEFT and RIGHT and the transformations

    BASE -> LEFT
    BASE -> RIGHT

a reconciliation is admissible only if it preserves the declared
intentions of both branches, except for losses or selections explicitly
authorized by the supplied interpretation policy.

Candidate rejection is not automatically a conflict of the entire
reconciliation problem.

Classification follows these mutually exclusive rules:

UNSUPPORTED:
    required structural operations, interpretation policy, or evidence
    contract are missing or outside the declared M001 domain.

AMBIGUOUS:
    evidence-consistent alternatives remain and differ materially
    in the requested result or outcome classification; no supplied
    evidence or policy justifies selecting one.

CONFLICT:
    after resolving the supported evidence and policy requirements,
    every admissible reconciliation alternative is rejected.

COMPATIBLE:
    an admissible accepted reconciliation is justified, and no
    unresolved alternative changes the requested result or outcome.

The ambiguity assessment concerns the requested observable result,
not merely the existence of multiple mathematical witnesses.

If multiple alternatives have equivalent requested outcomes, their
mere multiplicity does not require AMBIGUOUS.

A result cannot be COMPATIBLE solely because source and target
SHAPES forms are equal.

## 6. Frozen initial cases and policies

C1 — MOVE plus content edit.

    BASE contains root r and two sections p and q.
    LEFT moves p under q while preserving historical identity.
    RIGHT changes the content of historically identified p.

    The declared policy allows content to survive relocation and
    accepts the combined placement and content.

    Expected: COMPATIBLE.

    Countercase: if placement under q forbids RIGHT's content,
    the combined candidate is rejected; it cannot be accepted
    solely because MOVE and content change are different operations.

C2 — Incompatible updates to one property.

    A persistent section owns single-valued property k.
    BASE has k=0; LEFT requires k=1; RIGHT requires k=2.

    The declared policy requires both intentions and forbids
    automatic selection or combination.

    Expected: CONFLICT.

    A different explicit resolution policy may permit COMPATIBLE.
    The conflict is semantic, not a SHAPES theorem.

C3 — Consequential symmetric ambiguity.

    BASE has two structurally equal sibling occurrences.
    LEFT changes one occurrence to content L; RIGHT changes
    one occurrence to content R.

    There is no supplied historical association identifying
    either selected sibling across the branches.

    Under the declared exclusive-update policy, one possible
    association conflicts and another is compatible.

    Expected: AMBIGUOUS.

    No canonical index or arbitrarily optimal TPI witness may
    silently decide the historical association.

    Symmetric occurrences with an identical requested outcome
    do not necessarily imply AMBIGUOUS.

C4 — DELETE versus content edit.

    BASE contains a leaf section s with persistent identity.
    LEFT historically deletes s; RIGHT edits that same s.

    The declared policy forbids silently discarding either
    intention and rejects automatic delete/edit resolution.

    Expected: CONFLICT.

    Under an explicitly authorized deletion-wins policy,
    the same input may instead be COMPATIBLE.

    Subtree DELETE beyond a leaf is not part of this fixture.

## 7. Falsification criteria

M001 fails if the candidate model:

- infers historical identity only from SHAPES equality;
- treats a TPI complement as a proven historical death or birth;
- represents a genuine MOVE only as historical deletion and insertion;
- identifies a TPI witness with persistent vertex identity;
- silently chooses among consequential symmetric alternatives;
- declares semantic compatibility without consulting domain policy;
- accepts a merge that silently drops a required branch intention;
- returns overlapping outcome classifications;
- treats absent policy as proof of semantic conflict;
- treats all endpoint-equal witnessed paths as identical histories;
- requires modification of SHAPES normative semantics.

The outcome may be PASS, PARTIAL, FAIL or INCONCLUSIVE.
Negative results must be preserved.

## 8. Implementation boundary

First establish whether the model is coherent on the frozen cases.

Only then consider a minimal native C11 prototype with focused tests.

Do not promote experimental TPI files into stable APIs by copying
them wholesale. Reuse mathematical contracts before implementation.

No concurrency or CRDT guarantee is part of M001.
Concurrent reconciliation is a later phase, conditional on evidence.

## 9. References

- docs/reference/SPEC.md
- docs/research/theory/local-edit-path-completeness.md
- tools/research/tpi_algebra/REDUCTION.md
- tools/research/tpi_algebra/probe.py
- tools/research/tpi_algebra/structural_delta_micro/experiment.py
- tools/research/tpi_algebra/move_002/FORMAL_NOTES.md
- tools/research/tpi_algebra/move_002/RESULTS.md

This is a research contract, not a statement that the proposed
transformation engine already exists or has passed validation.
