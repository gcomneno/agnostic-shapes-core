# ASHES STE — EXP-004: consequential historical ambiguity

Status: FROZEN PROTOCOL — IMPLEMENTATION PENDING
Research layer: nonnormative
Predecessors: EXP-001, EXP-002, EXP-003
Language: C11

## Research question

Can a bounded C3 verifier evaluate explicitly supplied,
evidence-admissible historical associations and distinguish
consequential ambiguity from harmless multiplicity of
correspondences, without selecting an association by index,
enumeration order or structural equality?

## Scope

The BASE structural projection contains one root and two
structurally indistinguishable sibling occurrences.

LEFT changes one selected occurrence to opaque content L.
RIGHT changes one selected occurrence to opaque content R.

The supplied evidence does not determine whether the
selected occurrences share the same historical identity.

The verifier receives an explicit bounded collection of
candidate historical associations. It does not discover
historical identity, prove candidate completeness or derive
historical identity from SHAPES equality.

The interpretation owns the exclusive-update policy.

No general merge, TPI implementation change, SHAPES
semantic extension or merged document construction.

## Controlled alternatives

A — SAME OCCURRENCE:
  LEFT and RIGHT target one historical occurrence.
  Exclusive-update policy rejects two different contents.
  Expected alternative classification: CONFLICT.

B — DISTINCT OCCURRENCES:
  LEFT and RIGHT target different historical occurrences.
  The declared policy permits both changes.
  Expected alternative classification: COMPATIBLE.

Both A and B are supplied as admissible possibilities
with no evidence authorizing the selection of either.

Expected combined classification: AMBIGUOUS.

## Frozen controls

C3_CONSEQUENTIAL:
  Both A and B are admissible and materially disagree.
  Expected: AMBIGUOUS.

C3_REVERSED_ORDER:
  The same alternatives are supplied in reverse order.
  Expected: AMBIGUOUS.

C3_SINGLE_SAME:
  Evidence restricts candidates to A.
  Expected: CONFLICT within the supplied scope.

C3_SINGLE_DISTINCT:
  Evidence restricts candidates to B.
  Expected: COMPATIBLE within the supplied scope.

C3_HARMLESS_MULTIPLICITY:
  Multiple admissible associations share the same
  classification and the same requested material outcome.
  Expected: that shared classification, not AMBIGUOUS.

C3_MISSING_POLICY:
  A required policy decision is unavailable.
  Expected: UNSUPPORTED.

C3_UNDECIDED_POLICY:
  The interpretation cannot classify an interaction.
  Expected: UNSUPPORTED.

C3_NO_ALTERNATIVES:
  No evidence-admissible candidates are supplied.
  Expected: UNSUPPORTED.

C3_INVALID_ALTERNATIVE:
  A supplied candidate has an invalid edit contract.
  Expected: UNSUPPORTED.

C3_INCOMPLETE_EVIDENCE:
  Candidate completeness or admissibility has not been
  established by the caller.
  Expected: INCONCLUSIVE at the research evidence level;
  no definitive historical conclusion may be claimed.

## Measurements

- Classification of each admissible alternative.
- Combined classification under the declared contract.
- Invariance under candidate enumeration order.
- Distinction between consequential and harmless
  association multiplicity.
- Behavior with missing, undecided and invalid inputs.
- Explicit evidence-completeness assumptions.
- Preservation of existing 36 C11 regression checks.

The existing SteResult interface contains COMPATIBLE,
CONFLICT, AMBIGUOUS and UNSUPPORTED. INCONCLUSIVE is a
research outcome, not an additional SteResult value.

## Falsification criteria

EXP-004 fails if:

1. C3_CONSEQUENTIAL does not yield AMBIGUOUS.
2. Reordering candidates changes the result.
3. The verifier arbitrarily selects one association.
4. Harmless multiplicity is automatically labeled ambiguous.
5. Missing or undecided policy produces a definitive
   conflict or compatibility claim.
6. Invalid candidates are accepted as valid evidence.
7. The implementation claims historical completeness
   merely because candidates were enumerated.
8. A regression from EXP-001 through EXP-003 fails.
9. The implementation changes normative SHAPES semantics
   or treats structural equality as persistent identity.

No result criteria may be changed retroactively
to obtain a PASS.

## Outcome classes

PASS:
  All executable frozen criteria and regressions hold,
  under explicitly declared evidence assumptions.

FAIL:
  One or more frozen criteria are falsified.

INCONCLUSIVE:
  Required evidence is incomplete or cannot be validated.

UNSUPPORTED:
  A requested scenario exceeds the declared verifier
  or interpretation contract.

## Implementation boundary

Prefer a minimal standalone C11 verifier or a focused
test harness reusing existing ste_classify behavior.

Before implementation, establish whether existing
ste_classify already suffices for the executable cases.
Avoid duplicating the classifier without demonstrated need.

Do not modify SHAPES, PETRA, TPI, existing STE
interfaces or previously frozen protocols.

## Execution gates

1. Freeze and inspect this protocol.
2. Determine the minimal executable implementation.
3. Run the focused C3 controls.
4. Run the existing 36-check C11 regression.
5. Document observed results and evidence limitations.
6. Authorize commit and push as separate operations.
