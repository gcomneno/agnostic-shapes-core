# ADR 0002 — Independent Project Ownership Boundaries

## Status

Accepted architectural direction.

Documentation-only decision. Physical extraction is not yet implemented.

This ADR defines project ownership, not new SHAPES or interpretation
semantics. Normative semantics remain in their respective specifications.

## Decision

ASHES, PETRA, and COLLATZ are three distinct projects.

Their present coexistence in one repository and distribution is a
transitional packaging arrangement, not an ownership relationship.

### 1. ASHES

ASHES owns the interpretation-agnostic structural substrate:

- SHAPES finite rooted non-plane forms;
- structural identity, multiplicity, and intrinsic edits;
- structurally justified metrics and representation interfaces;
- Tensor View and STR as interpretation-neutral representations.

ASHES must not acquire arithmetic, prime/exponent, Collatz, AST,
or other consumer-specific semantics.

Tensor View belongs to ASHES only while its contract remains
independent of all interpretation policies.

### 2. PETRA

PETRA is an independent mathematical and software project consuming
ASHES contracts.

PETRA owns:

- the Prime Interpretation Problem (PIP);
- prime/exponent interpretation theory;
- its interpretation policies, including LRPE;
- policy-specific validation, numeric results, inverse operations,
  limitations, research, and releases.

PETRA may interpret SHAPES directly or consume neutral STR values.

PETRA must not redefine SHAPES identity, equality, or edits.

No practical value claim for ASHES follows automatically from
PETRA's mathematical results, and conversely.

### 3. COLLATZ

COLLATZ is a separate interpretation and research project consuming
ASHES contracts.

COLLATZ owns its mathematical interpretation, algorithms,
tests, limits, research claims, and eventual releases.

COLLATZ must not impose Collatz-specific fields or operations
on SHAPES or STR.

COLLATZ must not depend on PETRA merely to access ASHES.

## Dependency rule

Permitted:

    PETRA   -> ASHES
    COLLATZ -> ASHES

Prohibited as architectural dependencies:

    ASHES   -> PETRA
    ASHES   -> COLLATZ
    PETRA   -> COLLATZ
    COLLATZ -> PETRA

Direct SHAPES interpretation and interpretation-owned LAMBDA over
STR both remain admissible. No shared LAMBDA runtime framework is
introduced by this decision.

## Satellite classification

Resolver is an external structural consumer/satellite, not a fourth
core component and not part of PETRA or COLLATZ by default.

Its future distribution and ownership require a separate decision;
this ADR does not silently migrate Resolver into any of the three.

## Current implementation versus target ownership

Current implementation:

- one repository contains SHAPES, Tensor View, PETRA, and COLLATZ;
- the root Python distribution packages all four runtime packages;
- normative PETRA documentation and research history coexist here.

Target project ownership:

- ASHES owns only neutral structural contracts and infrastructure;
- PETRA and COLLATZ own independent consumer contracts and lifecycles.

The present package and repository layout must not be described as
already physically separated.

## Physical extraction gates

Before any extraction:

1. inventory source files, imports, tests, docs, release assets,
   and maintained consumers;
2. determine independent packaging, versioning, and CI boundaries;
3. preserve normative authority and historical provenance;
4. verify existing public behavior and regression coverage;
5. plan migration and cutover without circular dependencies;
6. authorize implementation separately;
7. verify installed artifacts and consumer compatibility.

No repository split, rename, package move, import rewrite, automatic
publication, or retrospective alteration of historical releases is
authorized by this ADR.

## Practical-value independence

ASHES is evaluated as a structural substrate for external consumers.

PETRA and COLLATZ are evaluated independently against their own
mathematical and practical objectives.

A valid formalization is not automatically an application.
A negative practical-value experiment does not invalidate an
independently established mathematical contract.

No new functionality follows automatically from this decision.
