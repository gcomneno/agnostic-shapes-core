# ASHES STE — TPI / Historical Association Boundary

Status: THEORETICAL RESEARCH NOTE — ISSUE #414
Authority: nonnormative
Prerequisites: STE-M001, R01, R02 and MOVE-002
Implementation: none
EXP-007: not started

## 1. Research question

How may structural TPI witnesses constrain a historical
association study without identifying structural
correspondence with persistent historical identity?

The objects of this note are deliberately distinct:

  phi : historical association candidate
  w   : structural TPI witness

Neither is reconstructed from SHAPES form equality.

## 2. Information ownership

FORM:
  Rooted unordered structural form owned by SHAPES.

CORRESPONDENCE:
  An explicit partial mapping subject to a selected
  structural validity discipline, such as TPI.

HISTORY:
  Persistent identity and provenance declared by an
  external historical model.

SEMANTICS:
  Content, interpretation policy and observables
  belonging to an external interpretation.

No implication from FORM or CORRESPONDENCE alone to
HISTORY or SEMANTICS is justified.

## 3. R02 interface

R02 defines a finite candidate universe U_H with
an externally assessed evidence predicate.

For accepted evidence E_acc:

  C_E = {phi in U_H : phi satisfies E_acc}

Its structural predicate S remains explicit and
parametric:

  A_E = {phi in C_E : S(phi)}

R04 does not replace the historical universe U_H
with an arbitrary collection of TPI witnesses.

If a study uses TPI, it must declare a relation:

  Bridge(phi,w)

and a selected collection W_TPI of legally valid
TPI witnesses between the relevant endpoints.

One possible structural predicate is:

  S(phi) iff there exists w in W_TPI
             such that Bridge(phi,w).

This is a *model choice*, not a universal law.
The meaning and soundness of Bridge must be justified
for the specific historical question.

In particular, Bridge(phi,w) need not be equality.

A different study may use TPI as supporting evidence
without imposing any TPI-derived exclusion on phi.

## 4. TPI structural witness conditions

For the rooted-tree TPI discipline considered in
the existing research, legal partial witnesses have:

- explicitly declared domain and image;
- matched roots when nonempty;
- domain and image closed under ancestry;
- a partial bijection on their selected occurrences;
- direct parent-child incidence preservation on
  matched occurrences.

These are requirements on w.

They do not automatically become requirements on
the historical association phi.

Validity of the selected TPI witness must be checked
against its actual source and target realizations.

No maximality or canonical choice follows merely
from legality of one witness.

## 5. Worked MOVE counterexample

Consider a concrete rooted tree with vertices:

  V = {r,a,p,q}

and source incidences:

  E = {(r,a),(a,p),(r,q)}

Move p from parent a to parent q, producing:

  E' = {(r,a),(r,q),(q,p)}

The historical association is the identity id_V:
all four vertices persist.

However, id_V is not a legal TPI witness because
the parent incidence for p changed.

The source and target can have the same SHAPES form,
so equality of those forms cannot resolve the
historical identity question.

For a nontrivial historical MOVE of subtree D,
the MOVE-002 result identifies the largest TPI
witness *constrained to the historical identity*
as id_(V minus D), in its declared concrete model.

That restricted maximum is NOT a maximum among all
alternative endpoint TPI witnesses.

A different endpoint witness may relate occurrences
differently while satisfying TPI constraints.

Therefore:

  HistoricalPersistence(p)
    does not imply TPIWitness(id_V).

Conversely:

  TPIWitness(w)
    does not imply HistoricalIdentity(w).

## 6. Witness-relative complements

For a selected TPI witness w, define its endpoint
complements relative to the domain and image of w.

Those complements record unmatched occurrences
*under that particular witness*.

They do not automatically prove historical births,
historical deaths or destruction of persistence.

A historically surviving vertex may fall outside
the domain or image of a valid partial TPI witness
because its incident structure changed.

The complement may change when a different legal
endpoint witness is selected.

Only independent historical evidence and its
declared provenance may support a birth/death claim.

## 7. Endpoint path completeness is not history

The existing local witnessed-edit path theorem is
about equivalence of paths with fixed structural
endpoint forms.

Its quotient does not faithfully preserve an
occurrence-survivor relation.

An elementary REMOVE followed by reverse ADD can
be congruent to an identity path, even though the
concrete removed occurrence is replaced by a new one.

Thus endpoint path equivalence cannot certify
the historical identity of surviving occurrences.

It also cannot select a preferred historical
association in the R02 candidate universe.

This limitation is independent of whether a
particular TPI endpoint witness is available.

## 8. Permitted uses

A selected TPI discipline may legitimately be used to:

- validate the structural legality of a proposed w;
- impose explicit, justified restrictions through a
  declared Bridge(phi,w) relation;
- describe a witness-relative unmatched complement;
- detect changes of direct incidence relative to a
  specified history-preserving identification;
- furnish structural evidence that is kept separate
  from historical attestations and semantic policy.

If a restriction removes candidate associations,
the model must state why this restriction is
appropriate for its historical question.

The R02 completeness theorem then remains relative
to the resulting declared S, not to actual histories.

## 9. Prohibited inferences

This note does not permit:

- treating a TPI witness as proof of persistence;
- equating witness complements with births or deaths;
- treating structural form equality as identity;
- requiring TPIValid(phi) for all historical MOVEs;
- selecting historical candidates by local indices
  or preferred endpoint isomorphisms;
- extending a fixed-history maximal-witness result
  to all alternative endpoint witnesses;
- claiming that endpoint-complete path equivalence
  reconstructs edit history;
- inferring semantic compatibility from TPI validity.

A false structural restriction can make an apparently
complete enumeration omit historically legitimate
candidates. Relative completeness does not repair
a misspecified admissibility predicate.

## 10. Qualification and limits

This document states an interface and reuses the
previously established MOVE-002 counterexample.

It does not independently prove a new general theorem
about all TPI endpoint witnesses.

It does not add a TPI implementation, a historical
identity resolver, a general merge operator, a
production STE API, or a SHAPES semantic extension.

R01 remains responsible for evidence assessment.

R02 remains responsible for finite relative
enumeration completeness.

R03 remains responsible for material outcome
equivalence and interpretation-specific observables.

EXP-004 historical completeness stays INCONCLUSIVE.
EXP-007 is not started.

## 11. Closure obligations

The research boundary is acceptable only if:

- phi and w retain distinct meaning and validity;
- the TPI bridge is explicit and never presumed;
- the MOVE counterexample is respected;
- fixed-history and alternative endpoint witnesses
  are not confused;
- complements remain witness-relative;
- path equivalence is not used to infer history;
- no SHAPES/TPI normative promotion occurs.

## References

- docs/research/ste-m001-contract.md
- docs/research/theory/local-edit-path-completeness.md
- tools/research/ste_001/HISTORICAL_EVIDENCE_MODEL.md
- tools/research/ste_001/FINITE_ASSOCIATION_MODEL.md
- tools/research/tpi_algebra/move_002/FORMAL_NOTES.md
