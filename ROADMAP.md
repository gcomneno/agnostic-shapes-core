
# SHAPES / PETRA Implementation Roadmap

## Authority

This roadmap orders implementation work after the canonical
[SHAPES core specification](docs/reference/SPEC.md).

It does not itself make behavior normative.

## Completed prerequisite — pending-work closure

Before the SHAPES/PETRA separation began:

- all open pull requests were resolved;
- all open issues were resolved or explicitly deferred/superseded;
- `main` was clean and aligned with `origin/main`.

The architectural migration therefore starts from a closed backlog.

## Phase 2.1 — normative SHAPES / PETRA boundary

Documentation only.

Establish:

```text
SHAPES = agnostic structural core
PETRA  = prime/exponent interpretation layer over SHAPES
PIP    = foundational theory inside PETRA
```

Also establish:

```text
PETRA -> SHAPES
future interpretation -> SHAPES

SHAPES -X-> PETRA
PETRA -X-> future interpretation
```

During this phase:

- do not change runtime behavior;
- do not rename the installed package;
- do not rename the CLI;
- do not rename serialized schemas;
- do not migrate Resolver;
- do not mass-rename historical research.

## Phase 2.2 — SHAPES intrinsic runtime

Introduce a new SHAPES runtime package containing only concepts justified by the agnostic core.

Initial runtime scope:

- one recursive node/form model;
- finite unordered child multiplicity;
- zero-child form;
- structural equality;
- intrinsic size;
- elementary `ADD`;
- elementary `REMOVE`;
- validation required by those contracts.

Do not port merely because it exists in `src/petra`.

Specifically, do not automatically admit:

- `Root(rank)`;
- `Term`;
- exponent `^` vocabulary;
- positional sibling identity;
- current PETRA schemas;
- `SPROUT`;
- `SHED`;
- `GRAFT`;
- `PRUNE`;
- representation-level `node_count`.

The first SHAPES tests should be derived from intrinsic semantics, not from compatibility spelling.

## Phase 2.3 — SHAPES representation boundary

Only after the intrinsic runtime is stable, decide which neutral representation interfaces SHAPES actually needs.

Possible concerns include:

- deterministic serialization;
- parsing;
- selectors or occurrence paths;
- operation-local targeting;
- public result types;
- CLI;
- schema namespace.

Do not silently reuse `1`, `C(r0^...)`, `^`, positional root ranks, or `petra.*` schemas as SHAPES contracts.

Every admitted representation concept must have an explicit structural justification.

### Admitted Phase 2.3 boundary

The first admitted SHAPES representation contract is intentionally narrow:

- `OccurrencePath` is a state-scoped selector into one current canonical
  runtime state;
- `iter_occurrences()` deterministically enumerates every current occurrence
  together with such a path;
- equal sibling forms remain separate occurrences when they represent
  separate child incidences;
- paths and traversal order remain representational and do not participate in
  structural identity;
- paths must be rederived after edits rather than treated as persistent
  occurrence identity.

No neutral SHAPES serialization, parser, CLI, schema namespace, witness
protocol, edit-result protocol, graph API, or additional metric has yet been
admitted.

Those capabilities remain deferred until a maintained consumer demonstrates
a requirement during dependent migration.

## Phase 2.4 — dependent migration

Classify repository dependents.

For Resolver:

- migrate structure-only search and metrics only when they can be expressed over SHAPES;
- keep prime assignment, integer conversion, factorization-driven construction, and numeric projections outside SHAPES;
- keep Resolver as a satellite during migration.

Research tools should migrate only when still maintained and when their semantics match the new layer boundary.

## Phase 2.5 — retire pre-separation `petra` core package

The current `src/petra` package disappears only after:

1. all agnostic core functionality required by maintained consumers exists in SHAPES;
2. SHAPES tests pass independently;
3. structure-only dependents no longer require `petra`;
4. compatibility behavior has been classified as:
   - removed;
   - migrated to SHAPES representation;
   - retained only as historical evidence;
   - reserved for future PETRA.

Do not leave `petra` as a permanent alias for SHAPES.

At the end of this phase there must be no dependency:

```text
SHAPES -> petra
```

## Phase 3 — PETRA interpretation layer

The Phase 2 retirement boundary is complete: the pre-separation structural
`petra` runtime has been removed.

Phase 3 begins with the normative interpretation contract in
`docs/reference/PETRA.md`.

No PETRA runtime implementation is admitted until that contract is accepted.

Only after the SHAPES boundary is executable and the old structural `petra` package has been retired may the new PETRA layer be introduced.

PETRA must depend on SHAPES.

Initial PETRA work begins from an explicit interpretation contract, not from restoring historical runtime vocabulary.

PIP belongs in this phase.

The PETRA contract must address at least:

- interpretation domain and codomain;
- prime assignment;
- exponent semantics;
- interpretation equivalence;
- injectivity conditions;
- reachable image;
- computability and partiality;
- reverse interpretation, if any;
- materialization limits.

PETRA interpretation must never redefine SHAPES equality or intrinsic `ADD / REMOVE`.

## Future sibling interpretations

Other interpretation layers may be added directly over SHAPES.

They must not be forced through PETRA.

Example:

```text
PETRA -----------\
                  \
Interpretation X ---> SHAPES
Interpretation Y ---/
```

A future meta-layer comparing interpretations is possible but is not part of the current roadmap.

## Historical material

Do not mass-rename:

- `docs/research/`;
- archived documents;
- historical PET/PETRA reports;
- release notes;
- changelog history;
- DOI/CITATION metadata;
- published version references.

Historical names identify historical contracts and evidence.

## Release boundary

The SHAPES separation is a breaking architectural transition.

Distribution, Python package, CLI, repository, and schema naming will be decided explicitly during their respective migration phases rather than inferred mechanically from the conceptual name.

No technical namespace rename is implied merely by Phase 2.1.

## Guiding rule

Structure belongs to SHAPES.

Prime/exponent interpretation belongs to PETRA.

PIP belongs inside PETRA.

Historical evidence remains historical.

Do not cross these boundaries for convenience.
