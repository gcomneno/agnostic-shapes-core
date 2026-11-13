# ASHES STE — EXP-007 Experimental Protocol

Status: FROZEN — V1
Issue: #415
Authority: nonnormative experimental research
Implementation: NOT STARTED
Scientific baseline: R01, R02, R03, R04

The fixture, policy, oracle-comparison and coverage
specifications are frozen for v1. Independent mathematical
review is complete: R01–R04 compatibility, fixture cardinalities
and mathematical expectations, material policy and oracle
independence specification, coverage and equivariance
specification, and diagnostic distinctions all PASS.
The F13 cycle defect is corrected and independently accepted.
The tables below are frozen EXPECTATIONS, not execution results.
Implementation has NOT STARTED; the experiment has not been
executed and no experimental results are yet established.
This freeze does not authorize implementation or execution.
The Git commit and an external SHA256 will identify v1;
the document does not embed its own checksum.

## 1. Research question

Can a bounded standalone enumerator return all and only
historical associations admitted by a declared finite
model, while preserving representation equivariance and
distinguishing historical, structural and material
outcome obligations?

This experiment tests model-relative enumeration.
It does not reconstruct actual historical identity,
prove general reconciliation soundness or establish
completeness over real-world histories.

## 2. Frozen-model candidate

Two snapshots have separate, identified roots and three
non-root concrete occurrences each:

  L = {l0,l1,l2}
  R = {r0,r1,r2}

Roots are paired by an external assumption and are not
members of the candidate association relation.

The candidate class H consists of total bijections
from L to R.

  U_H = {phi subseteq L x R : H(phi)}
  |U_H| = 3! = 6

All non-root occurrences are presumed to persist.
Births, deaths, replacement and partial associations
are outside this experimental instance.

Occurrence indices denote fixture presentation only.
They cannot determine historical identity or preference.

## 3. Evidence contract

Evidence records retain a stable record identifier,
source, target, polarity and provenance.

An external fixture assessment declares each record:

  ACCEPTED
  REJECTED
  UNRESOLVED

Only ACCEPTED REQUIRE and EXCLUDE records constrain
candidate membership.

  C_E = {phi in U_H :
         every accepted REQUIRE belongs to phi and
         every accepted EXCLUDE is absent from phi}

REJECTED records do not imply the opposite polarity.
UNRESOLVED records remain visible and cannot silently
be treated as false.

The synthetic provenance contract must identify source,
assessment rule and assumed trust; the experiment does
not independently verify provenance truth.

The enumeration of C_E is conditional on the accepted
record subset. Robustness to alternative resolutions
of unresolved records requires a separate comparison.

## 4. Structural profiles

Profile PRESERVED_OCCURRENCES:

  S_free(phi) = true

for a well-formed fixture and phi in U_H.

This profile permits historical persistence through
incidence changes, including genuine MOVE scenarios.

Profile UNCHANGED_INCIDENCE:

  S_inc(phi) iff transported(I_L, extended(phi)) = I_R

where extended(phi) maps the declared source root to
the declared target root and applies phi to all
non-root occurrences.

This profile is authorized only for fixtures that
explicitly assume unchanged direct incidence.

It is not a general rule for historical persistence
and must never exclude a legitimate MOVE merely
because the historical association is not a TPI
incidence-preserving witness.

The declared admissible candidate set is:

  A_E = {phi in C_E : S_profile(phi)}

Malformed snapshot trees, foreign handles, duplicated
vertex handles and invalid designated roots are rejected
before enumeration. Repeated evidence records are permitted
and do not change the effective accepted constraints.

## 5. Independent mathematical oracle

The reference oracle enumerates all 2^9 = 512 binary
relations on the nine possible L x R pairs.

It recognizes bijections using row/column occupancy:
exactly one pair in every source row and target column.

It then evaluates evidence and structure independently.

The future C11 enumerator must use a different
construction: triples of pairwise distinct destination
occurrences, representing the six permutations.

The reference must not import, reuse or translate
the enumerator's generator or filtering procedures.

Both sides report exact candidate sets for:

  U_H
  C_E
  A_E

Set membership is compared extensionally through
pairs of concrete occurrences, not through array
position or candidate enumeration order.

The six expected permutations are:

  012, 021, 102, 120, 201, 210

These are canonical fixture encodings, not assertions
about real historical identities.

The manually checked six-permutation table in section 7
is a frozen EXPECTATION accepted by completed independent
mathematical review,
not a measured oracle result.

## 6. Evidence configuration coverage

Each of the nine possible pairs may independently have:

  NONE
  REQUIRE
  EXCLUDE
  REQUIRE_AND_EXCLUDE

This produces 4^9 = 262144 accepted-polarity configurations;
all REQUIRE/EXCLUDE records in this matrix are ACCEPTED.

The fixed finite coverage matrix has exactly two instances:

| Named snapshot/profile instance | Profile | Configurations | Bijections per configuration | Tested candidate evaluations |
| --- | --- | ---: | ---: | ---: |
| star/S_free (two default stars) | S_free | 262144 | 6 | 1572864 |
| asymmetric tree/S_inc (F09 geometry on both sides) | S_inc | 262144 | 6 | 1572864 |
| Total | Two instances | 524288 instance/configuration pairs | 6 | 3145728 |

The reference separately classifies all 512 relations per
instance using row/column occupancy (1024 relation
classifications). It may retain its independently recognized
six bijections for evidence/structure evaluation over every
configuration: another 3145728 reference candidate evaluations.
This does not replace the tested side's six-permutation
candidate generation or permit sharing that generator.

This is a bounded finite-domain exhaustive check.
It is not a general scalability or performance claim.

Assessment and provenance cases are a distinct suite,
since accepted-polarity configurations cannot themselves
establish assessment reliability.

Repeated accepted records and reordered records must
produce the same effective candidate sets.

## 7. Named candidate fixtures

### Shared fixture defaults

Each snapshot has a separate designated root object,
root_L or root_R, and exactly three non-root occurrences
L = {l0,l1,l2}, R = {r0,r1,r2}; all eight vertex handles
are distinct and tagged by snapshot. Roots are externally
paired, excluded from L and R, and never identified by
an array index. Duplicate vertex handles are invalid;
repeated references to a handle in evidence are permitted.

Unless explicitly overridden, both snapshots are fixed
stars with incidences root_L -> li and root_R -> ri for
i = 0,1,2, the profile is S_free, and evidence is empty.
Every unqualified REQUIRE/EXCLUDE below is ACCEPTED.
Each record has a stable fixture/record identifier and
synthetic provenance: origin EXP-007 fixture declaration,
scope the stated snapshot pair and association, trust
assumed solely for this finite model. The external synthetic
assessment rule uses the declared status, default ACCEPTED;
REJECTED and UNRESOLVED are explicit overrides. Neither
provenance nor assessment asserts actual historical truth.

Repeated records, including repeated presentations of the
same record and distinct records attesting the same pair
and polarity, are permitted. They preserve effective
constraints; record identity and provenance remain auditable.

### Synthetic material policy (declared before fixtures)

Material fixtures use the fixed star pair and S_free,
unless explicitly overridden. Every non-root occurrence
has one single-valued property with value domain
V = {0,lambda,rho}, where all three values are distinct.
Initial values on both sides are 0; roots have no material
cell in this model. A final material is a map M : L -> V.

Every retained required update is an equality on final M:
left li := v requires M(li) = v; right rj := v is transported
to l_(phi^-1(j)) := v, requiring M(phi^-1(rj)) = v.
An unchanged source cell, targeted by no retained update,
must preserve 0. No additional writes, merge, intention
loss or selection is allowed unless explicitly authorized
in that fixture. In particular, single-valuedness does not
permit two different required values at the same cell.

For each supported fixture let D be its complete finite
set of authorized policy decisions. M01–M03 have D = {strict}
with no losses; M04 declares exactly two decisions below.
For d in D, retain all updates except those explicitly
waived by d, and let T_phi,d be their transported source
targets. Define the complete, total Boolean predicate on V^L:

  P_phi,d(M) iff
    every retained left update li := v has M(li) = v, and
    every retained right update rj := v has M(phi^-1(rj)) = v, and
    every l in L minus T_phi,d has M(l) = 0.

There are no further material conditions for M01–M04.

  P_phi(M) = OR over d in D of P_phi,d(M)
  W_phi,d = {M in V^L : P_phi,d(M)}
  W_phi = {M in V^L : P_phi(M)}

The supported per-decision outcome set is all ACCEPT(M)
for M in W_phi,d, or {REJECT} if W_phi,d is empty.
Preserve the decision and retained/waived intentions with
each witness, even when Q observes only ACCEPT(M) or REJECT.
The per-association set retains outcomes from every d in D.
Unsupported policy gives no total P_phi; it gives neither
an empty W_phi nor a certified REJECT.

Certify rejection only after exhaustive evaluation of all
27 assignments in V^L with fully resolved policy: W_phi,d
must be empty for a decision-level rejection, and W_phi
empty for rejection of the association under all decisions.

F01 — No evidence:
  star-shaped snapshots, S_free
  Expected |C_E| = 6, |A_E| = 6.

F02 — REQUIRE(l0,r0):
  star-shaped snapshots, S_free
  Expected 2/2.

F03 — REQUIRE(l0,r0), REQUIRE(l1,r1):
  star-shaped snapshots, S_free
  Expected 1/1.

F04 — EXCLUDE(l0,r0):
  star-shaped snapshots, S_free
  Expected 4/4.

F05 — REJECTED REQUIRE(l0,r0):
  no accepted constraints, S_free
  Expected 6/6.

F06 — REQUIRE(l0,r0), REQUIRE(l0,r1):
  inconsistent evidence, expected 0/0.

F07 — REQUIRE(l0,r0), EXCLUDE(l0,r0):
  inconsistent evidence, expected 0/0.

F08 — EXCLUDE(l0,r0), EXCLUDE(l0,r1),
      EXCLUDE(l0,r2):
  inconsistent evidence, expected 0/0.

F09 — Same rooted structural shape on both sides:
  root -> 0, 0 -> 1, root -> 2;
  S_inc, no evidence.
  Expected 6/1.

F10 — Same shape as F09:
  source root_L -> l0, l0 -> l1, root_L -> l2;
  target root_R -> r0, r0 -> r1, root_R -> r2;
  S_inc, REQUIRE(l0,r2), REQUIRE(l1,r1).
  The only evidence-admissible candidate is 210.
  It fails S_inc: |C_E| = 1, |A_E| = 0;
  evidence is consistent, structure unsatisfiable.

F11 — Genuine MOVE:
  source root_L -> a_L, a_L -> p_L, root_L -> q_L;
  target root_R -> a_R, root_R -> q_R, q_R -> p_R;
  S_free, with three ACCEPTED REQUIRE records:
  a_L -> a_R, p_L -> p_R and q_L -> q_R, each with the
  synthetic provenance and assessment assumptions above.
  For encoding only, (l0,l1,l2) = (a_L,p_L,q_L) and
  (r0,r1,r2) = (a_R,p_R,q_R). U_H still has six members;
  accepted evidence fixes C_E = A_E = {012}, expected 1/1.
  This historical identity fails direct-incidence
  preservation because p changes parent. Structural
  isomorphism alternatives may exist (here 210), without
  establishing historical identity or displacing 012.

F12 — UNRESOLVED REQUIRE(l0,r0):
  S_free and the fixed (frozen as fixture data) pair of
  star snapshots; the unresolved record contributes no
  accepted constraint. Conditional enumeration 6/6.
  Holding snapshots, U_H and S_free fixed, if that REQUIRE
  becomes ACCEPTED, C_E = A_E = {012,021} (2/2);
  if REJECTED, all six remain (6/6), with no negation added.
  Test both status resolutions as separate sensitivity cases.
  These are candidate-set sensitivity expectations only.
  No robustness claim is made for an unspecified historical
  query; such a claim needs a declared query and a separate
  comparison across permitted evidence resolutions.

F13 — Invalid input:
  Four separate variants of the default input:
    duplicated handle: replace l1 with l0 in the vertex list;
    foreign handle: REQUIRE(l_foreign,r0), l_foreign not in L;
    invalid tree: set the complete final source incidence set to
      I_L = {
        root_L -> l2,
        l0 -> l1,
        l1 -> l0
      }, containing a directed cycle l0 -> l1 -> l0
      disconnected from the designated root;
    invalid root: designate an object outside the snapshot.
  Each is INVALID_INPUT and UNSUPPORTED before enumeration.
  No candidate-set cardinality is applicable.

F14 — Contradictory accepted REQUIREs sharing a target:
  REQUIRE(l0,r0), REQUIRE(l1,r0), expected 0/0.

Record-presentation suite: for each of F02, F03, F06–F08,
F10, F11 and F14, test all record orders; also repeat each
record once, in place, in the declared order. Both variants
must preserve the exact C_E and A_E sets. Repeated evidence
is never confused with F13's invalid duplicated vertices.
This is 23 record-order cases plus eight duplication cases,
31 cases total, without crossing the two transformations.

### Manually checked six-permutation candidate table

Frozen EXPECTATIONS accepted by completed independent mathematical review.
Encoding abc means phi(l0)=ra, phi(l1)=rb, phi(l2)=rc.
A means membership in both C_E and A_E; C means membership
in C_E only; – means membership in neither. Every row is
in U_H. F13 has no enumerated candidate set.

| phi | F01 | F02 | F03 | F04 | F05 | F06–F08, F14 | F09 | F10 | F11 | F12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 012 | A | A | A | – | A | – | A | – | A | A |
| 021 | A | A | – | – | A | – | C | – | – | A |
| 102 | A | – | – | A | A | – | C | – | – | A |
| 120 | A | – | – | A | A | – | C | – | – | A |
| 201 | A | – | – | A | A | – | C | – | – | A |
| 210 | A | – | – | A | A | – | C | C | – | A |
| C_E/A_E counts | 6/6 | 2/2 | 1/1 | 4/4 | 6/6 | 0/0 | 6/1 | 1/0 | 1/1 | 6/6 |

These exact sets and counts are expectations, not measured
results. Independent mathematical review is complete and accepted.

## 8. Diagnostic distinctions

MISSING_EVIDENCE:
  No pertinent evidence record is available.
  It is not an EXCLUDE and does not prevent
  conditional relative enumeration.

EVIDENCE_INCONSISTENT:
  iff C_E is empty (for well-formed input).

STRUCTURALLY_UNSATISFIABLE:
  iff C_E is nonempty but A_E is empty.

ASSESSMENT_UNRESOLVED:
  One or more relevant records lack a final
  external assessment.

INVALID_INPUT:
  The declared finite model is not well formed.

EVIDENCE_INCONSISTENT and STRUCTURALLY_UNSATISFIABLE
cannot coexist: test C_E first, then A_E only if C_E is
nonempty. Other diagnostics, such as ASSESSMENT_UNRESOLVED,
may coexist when independently supported. INVALID_INPUT
prevents enumeration; do not misreport its absence of
candidate sets as either empty-set diagnostic.
No diagnostic, alone or in combination, implies an STE
merge CONFLICT; separate reconciliation obligations apply.

An unresolved assessment yields conditional
candidate results, not an unconditional conclusion.

## 9. Equivariance and order independence

For every pair of independent renamings of the three
non-root occurrences:

  sigma_L in S3
  sigma_R in S3

the transformed relation is:

  T(phi) = sigma_R o phi o inverse(sigma_L)

Transport evidence, snapshot incidence, source/target
selectors and provenance references consistently.

Verify:

  H'(T(phi)) = H(phi)
  EvidenceSatisfied'(T(phi)) =
      EvidenceSatisfied(phi)
  S'(T(phi)) = S(phi)
  A_E' = T[A_E]

For material transport, define:

  M' = M o inverse(sigma_L)
  T_out(ACCEPT(M)) = ACCEPT(M')
  T_out(REJECT) = REJECT.

Transport each authorized policy decision, including its
retained/waived intentions. Require exact per-association,
per-decision outcome-set agreement under T_out and exact
transported observable-class agreement, not just equal
class counts. Within an unchanged fixture, distinct maps
remain distinct; renaming is not a quotient that equates
different material outcomes.

The fixed transformation suites are:

| Suite | Selected fixtures | Cases per fixture | Total cases |
| --- | --- | ---: | ---: |
| Independent label renamings | F01–F12, F14 (all well-formed candidate fixtures) | 6 x 6 = 36 | 468 |
| Material label renamings | M01–M04 | 36 | 144 |
| Independent vertex layouts | F01, F09, F10, F11 | 4! x 4! = 576 | 2304 |
| Six-association presentation orders | M01–M03 | 6! = 720 | 2160 |
| Two-outcome presentation orders | M04 | 2! = 2 | 2 |

Layout permutations move all four vertices on each side;
roots remain designated objects, including when stored
away from array index zero. Incidence, evidence and selectors
follow those objects. Each suite starts from its named
fixture, without composing it with the other suites.

For k distinct presented candidate alternatives the number
of orders is k!, not always 720. M01–M03 present all six
associations, including M03's rejected material alternatives;
do not deduplicate observable classes before ordering.
M04 has one association and two authorized material outcomes:
test both outcome orders while retaining both decisions.

These separate suites do not claim their universal cross
product, nor transformations of every polarity configuration.

No result may depend on the first candidate or
on a particular local storage index.

## 10. Synthetic material observable

This interpretation uses the synthetic domain, equality
updates, preservation rules and total supported predicates
declared before the fixtures in section 7.

The declared query Q observes rejection or acceptance
and the resulting values at each source occurrence:

  O_Q(outcome) = REJECT

or:

  O_Q(outcome) = ACCEPT(M)

where M maps L to V.

Two supported outcomes are equivalent iff their tags
agree and accepted result mappings M are extensionally
equal over concrete source occurrences.

This relation must satisfy reflexivity, symmetry
and transitivity on the supported observable domain.

An undefined observable is not silently equivalent
to a defined one.

### Independent material comparison

The tested side directly constructs the complete
per-association, per-authorized-decision outcome sets from
the declared update equalities, frame rules and explicit
loss authorizations. It must preserve every authorized
alternative rather than select the first witness.

The reference independently enumerates all 27 maps M in V^L
for each association and authorized decision and checks
the complete P_phi,d, including unchanged-cell preservation.
It also checks P_phi and W_phi across the full declared D.
Retain every accepting assignment and its satisfied
obligations. For an empty W_phi,d, retain all 27 failing
assignments and their violated conjuncts as the rejection
certificate; rejection of the association requires this
for every authorized decision. A partial search, unknown
policy or undefined observable is never a rejection proof.

Compare exact outcome sets for each association and each
authorized policy decision, including the retained/waived
intentions and acceptance/rejection witnesses. Compare
observable partitions only after these sets agree.
Matching counts or SteResult values is insufficient.

Do not share candidate generator, candidate filtering or
material solver logic between implementation and oracle.
They may share only the declarative fixture inputs, value
symbols and serialization contract. The reference must
not call or translate the tested material constructor;
its 27-assignment predicate checks remain independent.

## 11. Material fixtures

M01 — Harmless association multiplicity:
  left update l0 := lambda.
  No evidence; all six associations are admissible.
  Under strict policy, each has the sole material
  ACCEPT(lambda,0,0). Six accepted outcomes across
  associations, one observable class.

M02 — Equal classification, distinct materials:
  right update r0 := rho.
  No evidence; strict policy, all six associations.
  All six associations yield accepted outcomes,
  with rho exactly at phi^-1(r0), all other cells 0.
  Exactly three material classes, two associations each.
  Equal COMPATIBLE classification does not
  establish material equivalence.

M03 — Consequential mixed alternatives:
  left update l0 := lambda and right update
  r0 := rho, both mandatory.
  No evidence; strict policy, all six associations.
  Exactly 012 and 021 have REJECT: they require both
  distinct values at l0. The four accepted outcomes split
  into ACCEPT(lambda,rho,0) for 102,201 and
  ACCEPT(lambda,0,rho) for 120,210.
  Three observable classes total, including REJECT.

M04 — One association, multiple outcomes:
  Accepted REQUIRE(l0,r0), REQUIRE(l1,r1), REQUIRE(l2,r2)
  with the shared synthetic provenance fix association
  012 without changing U_H; S_free, fixed star snapshots.
  Concurrent mandatory updates are left l0 := lambda and
  right r0 := rho, transported under 012 to l0 := rho.
  Exactly two alternative intention losses are authorized:
    d_lambda: retain lambda and explicitly waive rho;
    d_rho: retain rho and explicitly waive lambda.
  W_012,d_lambda = {(lambda,0,0)} and
  W_012,d_rho = {(rho,0,0)}.
  Expected accepted materials are (lambda,0,0) and
  (rho,0,0), two observable classes. Keep both outcomes
  when no further justified policy selection exists;
  authorization of two losses does not itself choose one.

M05 — Separate unsupported and inconclusive cases:
  M05-P: use M04's snapshots, identity evidence and update
  inputs, but omit the required retention/loss policy and
  complete D. Policy evaluation is UNSUPPORTED: there is
  no total P_phi or certified empty W_phi. The scientific
  material-equivalence claim is INCONCLUSIVE, not REJECT.
  M05-O: use M01's fully supported policy and materials,
  but a query requesting an undeclared extra property.
  Its observable is undefined (OBSERVABLE_UNDEFINED);
  the comparison is unsupported and the scientific
  equivalence claim INCONCLUSIVE. Do not invent a value,
  form an equality class or discard valid material witnesses.
  M05-I: use M01's supported policy and defined Q, but an
  incomplete independent comparison. The scientific claim
  is INCONCLUSIVE due to incomplete coverage, even though
  policy and observable are supported. This is neither an
  unsupported policy nor a rejected material alternative.

For each association, enumerate all relevant
outcomes rather than choosing one by index.

### Manually checked material-outcome table

Frozen EXPECTATIONS accepted by completed independent mathematical review.
Tuples list values at (l0,l1,l2), and A(x,y,z) abbreviates
ACCEPT(x,y,z). Each cell is the exact per-association
outcome set; – means the association is not in that
fixture's A_E, not REJECT. M04's two members retain their
distinct d_lambda/d_rho authorizations.

| phi | M01 (strict) | M02 (strict) | M03 (strict) | M04 (both decisions) |
| --- | --- | --- | --- | --- |
| 012 | {A(lambda,0,0)} | {A(rho,0,0)} | {REJECT} | {A(lambda,0,0), A(rho,0,0)} |
| 021 | {A(lambda,0,0)} | {A(rho,0,0)} | {REJECT} | – |
| 102 | {A(lambda,0,0)} | {A(0,rho,0)} | {A(lambda,rho,0)} | – |
| 120 | {A(lambda,0,0)} | {A(0,0,rho)} | {A(lambda,0,rho)} | – |
| 201 | {A(lambda,0,0)} | {A(0,rho,0)} | {A(lambda,rho,0)} | – |
| 210 | {A(lambda,0,0)} | {A(0,0,rho)} | {A(lambda,0,rho)} | – |
| Observable classes | 1 | 3 | 3 (including REJECT) | 2 |

M05-P, M05-O and M05-I retain their separate unsupported,
undefined and scientific INCONCLUSIVE expectations above;
they are not added to the supported observable partition.
Acceptance needs a verified valid material witness.
Rejection needs the exhaustive 27-assignment certificate
specified above. No table entry is an execution result.

The original EXP-004 harmless-multiplicity
fixture remains a CALLER_ASSUMPTION and is not
retroactively promoted to verified equivalence.

## 12. Falsification conditions

One occurrence of any of the following falsifies
the respective experimental obligation:

- An admissible candidate omitted.
- An inadmissible candidate included.
- A duplicated emitted candidate.
- An incorrect C_E versus A_E distinction.
- An invalid input silently accepted.
- Incorrect treatment of missing, rejected
  or unresolved evidence.
- Any equivariance or order-dependence violation.
- A legitimate MOVE rejected by S_free as
  though historical identity required TPI validity.
- An alternative material outcome omitted.
- An accepted material outcome without a
  valid witness.
- Rejection despite an admissible material witness.
- Equivalence inferred only from classification.
- COMPATIBLE or CONFLICT inferred from
  an empty A_E without separate obligations.

Incomplete execution, missing essential policy
or unresolved evidence produces INCONCLUSIVE
for the affected scientific claim, never PASS.

A correctly diagnosed negative fixture can PASS
as a test without being a positive STE outcome.

## 13. Measurements and evidence

Record at least:

- Counts of U_H, C_E and A_E.
- Exact candidate-set mismatches.
- False positives, false negatives and duplicates.
- Accepted, rejected and unresolved record counts.
- Structural and evidence diagnostic categories.
- Renaming and ordering violations.
- Per-association material outcomes.
- Exact per-decision material outcome-set mismatches,
  retained/waived intentions and witness certificates.
- Observable equivalence classes.
- Invalid material witnesses.
- Completed and skipped fixture counts.
- Completed versus required cases in each finite coverage
  suite, without inferring untested cross products.
- Frozen protocol identity and code revision.
- Compiler, strict C11 flags and executed commands.

All negative and inconclusive evidence must be
retained in EXP007_RESULTS.md.

No performance observation supports arbitrary
unbounded enumeration.

## 14. Implementation entry conditions

Implementation is forbidden until:

1. This protocol is reviewed and frozen.
2. The candidate, evidence and structural
   domains are fixed and internally consistent.
3. Named fixture expectations are independently
   checked, including the MOVE example.
4. The two oracle strategies are reviewed
   for implementation independence.
5. Outcome policy and observables are fixed.
6. Coverage counts and falsification
   conditions are explicitly approved.
7. The frozen protocol has an immutable checksum.

After these gates, the intended minimal implementation
is standalone C11 with a maximum of six candidates,
separate filter functions and focused test executable.

No dynamic allocation, TPI engine, general
reconciliation engine or production API is required.

## 15. Artifacts

  EXP007_PROTOCOL.md
  EXP007_FIXTURES.json
  exp007_reference.py
  historical_associations.c
  test_exp007.c
  EXP007_RESULTS.md
  exp007_evidence.json

This step freezes the protocol as v1 after completed independent
mathematical review. All other artifacts remain proposed.
Implementation has NOT STARTED and the experiment has not been
executed; future experimental results remain unestablished.
The implementation entry conditions in section 14 remain in force.

## 16. Explicit limitations

The experiment cannot establish:

- completeness over actual historical events;
- trustworthiness of provenance attestations;
- identity discovery from structural equality;
- equivalence of arbitrary material interpretations;
- general STE merge soundness;
- concurrent or CRDT correctness;
- normative changes to SHAPES or TPI.

EXP-004 historical completeness stays INCONCLUSIVE.
EXP-004 material equivalence remains CALLER_ASSUMPTION.
No actual-history completeness, general merge proof or
normative SHAPES/TPI change follows from this protocol.

The baseline EXP-006 regression evidence is retained,
but it is not a substitute for EXP-007 qualification.

## References

- docs/research/ste-m001-contract.md
- tools/research/ste_001/HISTORICAL_EVIDENCE_MODEL.md
- tools/research/ste_001/FINITE_ASSOCIATION_MODEL.md
- tools/research/ste_001/TPI_HISTORY_BOUNDARY.md
- tools/research/ste_001/MATERIAL_OUTCOME_EQUIVALENCE.md
- tools/research/ste_001/EXP004_PROTOCOL.md
- tools/research/ste_001/EXP005_PROTOCOL.md
- tools/research/ste_001/EXP006_PROTOCOL.md
