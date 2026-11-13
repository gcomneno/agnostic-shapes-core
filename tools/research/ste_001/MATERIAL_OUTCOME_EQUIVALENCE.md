# ASHES STE — Material Outcome Equivalence

Status: THEORETICAL RESEARCH NOTE — ISSUE #413
Authority: nonnormative
Prerequisites: STE-M001, R01 and R02
Related boundary: R04
Implementation: none
EXP-007: not started

## 1. Research question

When do distinct admissible historical associations
lead to the same requested material result, and when
does their multiplicity constitute consequential
ambiguity?

An equal STE classification is not, by itself,
evidence of equal material outcomes.

## 2. Ownership boundaries

FORM belongs to SHAPES.

CORRESPONDENCE is a declared structural mapping,
possibly constrained by TPI.

HISTORY is externally supplied association and
provenance evidence.

SEMANTICS owns content, reconciliation policies,
requested observables and material equivalence.

No SHAPES form equality or TPI witness determines
semantic equivalence or historical persistence.

## 3. Association domain

Reuse the finite R02 model.

Let:

  U_H = declared historical association universe

  C_E = {phi in U_H : phi satisfies E_acc}

  A_E = {phi in C_E : S(phi)}

E_acc and its assessment are governed by R01.

S is the declared structural predicate. R04 explains
why TPI constraints cannot silently establish history.

This note does not modify U_H or infer evidence
from a preferred correspondence.

Before any result comparison, evidence consistency,
structural admissibility and assessment completeness
must be evaluated under their respective contracts.

In particular:

  A_E = empty

does not imply that all reconciliation alternatives
have been substantively rejected.

## 4. Outcome domain

For each phi in A_E, let R(phi) denote a declared
set of possible reconciliation outcomes under
the applicable interpretation and policy.

An outcome records at least:

- its STE outcome classification where defined;
- the requested material result or its declared
  observable representation where available;
- the preservation obligations and any explicitly
  policy-authorized losses relevant to that result.

A single historical association may admit multiple
outcomes. R(phi) must not be silently replaced by
one conveniently selected outcome.

A claimed unique outcome must be justified,
possibly only up to the requested equivalence.

The domain of all evaluated outcomes is:

  R_all = union over phi in A_E of R(phi).

An absent outcome, an unsupported evaluation and
a rejected candidate are not interchangeable.

## 5. Requested observable

Before evaluating any candidate, the interpretation
declares a query Q and a material observable O_Q.

O_Q specifies which parts of a reconciliation
outcome are relevant to the requested result.

It must include distinctions needed by Q:
for example, whether an outcome is accepted or
rejected, and the requested material values
where an accepted result exists.

An observable may intentionally ignore irrelevant
details, but that choice must be declared.

An excessively coarse observable can conceal
material differences, so harmlessness is always
relative to Q and its declared observation contract.

## 6. Equivalence contract

Let X_Q be the set of supported, defined
observable results for Q.

The interpretation declares an equivalence
relation approximately_Q on X_Q satisfying:

Reflexivity:
  x approximately_Q x

Symmetry:
  x approximately_Q y
  implies y approximately_Q x

Transitivity:
  x approximately_Q y and y approximately_Q z
  imply x approximately_Q z.

For supported outcomes a and b:

  a equivalent_Q b

iff:

  O_Q(a) approximately_Q O_Q(b).

The relation is not defined merely as equality
of SteResult values or equality of SHAPES forms.

If an outcome has no defined observable under
the selected interpretation contract, this
absence must be handled as unsupported or
inconclusive rather than equated to a supported
outcome.

## 7. Material outcome multiplicity

Assume:

- A_E is nonempty;
- all relevant associations have been evaluated;
- required interpretation and policy decisions exist;
- all requested material observables are defined;
- all possible outcomes relevant to Q are included;
- unresolved historical evidence cannot silently
  change the asserted conclusion.

Partition R_all into equivalence classes using
equivalent_Q.

Harmless multiplicity relative to Q:
  R_all has exactly one equivalence class.

Consequential multiplicity relative to Q:
  R_all has at least two equivalence classes
  and no declared evidence or policy authorizes
  choosing only one.

Under the M001 classification contract, supported
unresolved consequential alternatives justify
STE_AMBIGUOUS.

One equivalence class does not automatically
justify STE_COMPATIBLE.

COMPATIBLE additionally requires an admissible,
accepted outcome and its preservation obligations.

CONFLICT requires justified rejection of every
relevant admissible reconciliation alternative
after resolving evidence and policy requirements.

Neither classification may be inferred vacuously
from an empty A_E.

The note does not alter existing SteResult values.

## 8. Explicit policy selection

The interpretation may explicitly authorize an
intention loss or a selection among alternatives.

Such authorization must identify its scope
and the obligations being relaxed.

An arbitrary enumeration order, local array
position or preferred TPI witness cannot
substitute for this authorization.

A permitted selection changes the requested
decision contract and must be recorded before
claiming that consequential alternatives have
been resolved.

A selection policy does not establish that a
structurally invalid result is admissible.

## 9. Worked example: harmless multiplicity

Suppose two distinct admissible associations
phi_a and phi_b produce accepted results a and b.

Let the declared query Q request only a material
value v, and suppose the interpretation establishes:

  O_Q(a) = v
  O_Q(b) = v

with no other distinction required by Q.

Then a equivalent_Q b, and the two association
witnesses contribute one observable class.

This is harmless multiplicity relative to Q,
conditional on completeness of the relevant
associations and outcomes.

It is not evidence that phi_a and phi_b encode
the same historical identity.

## 10. Worked example: equal classification,
## different material outcomes

Suppose two admissible associations yield:

  classification(a) = STE_COMPATIBLE
  classification(b) = STE_COMPATIBLE

but Q requests the resulting content at a
historically identified target, and the
interpretation establishes:

  O_Q(a) = "L"
  O_Q(b) = "R"

with "L" not approximately_Q "R".

These outcomes are consequentially different
despite identical STE classifications.

Without evidence or policy resolving their
choice, the combined result is AMBIGUOUS
under the declared supported comparison.

## 11. Worked example: conflict versus compatible

In the EXP-004 C3 fixture, two externally
supplied association alternatives yield:

SAME OCCURRENCE:
  Different exclusive updates target one
  historical occurrence; policy rejects.

DISTINCT OCCURRENCES:
  The declared policy allows both changes.

The per-alternative classifications are
CONFLICT and COMPATIBLE respectively.

If both alternatives are evidence-admissible
and their outcome distinction is requested,
no association may be selected arbitrarily.

The combined classification is AMBIGUOUS
under the original supported C3 conditions.

This reproduces EXP-004's classification
observation, not a proof of historical
candidate completeness.

## 12. Multiple outcomes per association

Let phi be one admissible historical
association with two supported results a,b.

If a and b differ under approximately_Q,
the requested outcome remains materially
underdetermined even though phi is fixed.

An implementation must evaluate both, or
justify their unique observable class.

Historical association completeness alone
does not establish outcome completeness.

This distinction is required before claiming
that all observable alternatives were
considered.

## 13. Limits of EXP-004 evidence

The EXP-004 harmless-multiplicity fixture
supplies the same distinct alternative twice.

It verifies classifier behavior under
duplicated supplied candidates.

It does not independently show that two
different historical associations yield
equivalent material results.

The fixture explicitly records:

  MATERIAL_OUTCOME_EQUIVALENCE=CALLER_ASSUMPTION

That statement remains true of EXP-004.

The mathematical examples in this note
define conditions and consequences; they
are not new executable experimental evidence.

Historical completeness for EXP-004 remains
INCONCLUSIVE.

## 14. Required closure properties

A valid material-equivalence claim requires:

- a fixed candidate universe and accepted evidence;
- a declared structural admissibility predicate;
- an explicit requested observable O_Q;
- an interpretation-owned equivalence relation;
- its reflexive, symmetric and transitive laws;
- coverage of all relevant outcomes per candidate;
- an explicit basis for any policy selection;
- separately justified positive or conflict
  classification obligations.

Unresolved essential inputs do not permit
a definitive result.

## 15. Scientific limits

This note does not establish:

- factual reliability of historical attestations;
- completeness over real historical events;
- autonomous persistent-identity reconstruction;
- general semantic equivalence of SHAPES forms;
- a complete realization or merge algorithm;
- general merge soundness or completeness;
- concurrency or CRDT guarantees;
- any production runtime behavior.

It does not change STE interfaces, TPI
implementations or normative SHAPES semantics.

## 16. Research handoff

R01 owns the historical evidence assessment.

R02 owns the finite association universe and
relative enumeration completeness.

R04 owns the TPI/HISTORY correspondence boundary.

This note defines the interpretation-owned
observable-equivalence boundary required
before experimentally evaluating harmless
or consequential association multiplicity.

EXP-007 requires its own frozen protocol
before any C11 executable research.

## References

- docs/research/ste-m001-contract.md
- tools/research/ste_001/HISTORICAL_EVIDENCE_MODEL.md
- tools/research/ste_001/FINITE_ASSOCIATION_MODEL.md
- tools/research/ste_001/TPI_HISTORY_BOUNDARY.md
- tools/research/ste_001/EXP004_PROTOCOL.md
- tools/research/ste_001/test_exp004.c
