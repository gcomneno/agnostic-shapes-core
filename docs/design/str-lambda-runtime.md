# STR / LAMBDA Runtime Design — M0

## Status

Accepted implementation design.

Non-normative.

This document translates the promoted STR / LAMBDA architecture into a minimal
runtime design.

It does not itself modify SHAPES semantics, PETRA semantics, or public runtime
behavior.

Implementation begins only in later milestones.

---

## 1. Goal

Introduce the minimum runtime machinery needed to represent the promoted path:

```text
SHAPES
    ↓ Tensor View
STR
    ↓ interpretation-owned LAMBDA
interpretation domain
```

without:

- contaminating SHAPES with representation-specific semantics;
- embedding PETRA semantics into STR;
- making STR mandatory for all interpretations;
- forcing an immediate PETRA migration;
- inventing a generic interpretation framework before multiple runtime
  consumers demonstrate a common interface.

---

## 2. Current runtime baseline

The distribution currently exposes two Python packages:

```text
shapes
petra
```

The relevant current dependency is:

```text
petra -> shapes
```

SHAPES owns structural state.

PETRA owns LRPE interpretation semantics.

The current PETRA runtime accepts `Shape` directly.

M0 does not change any of these runtime contracts.

---

## 3. New runtime package boundary

The new representation layer will live in a separate package:

```text
src/
├── shapes/
├── tensor_view/
└── petra/
```

The intended dependency direction is:

```text
tensor_view -> shapes
petra       -> shapes
```

and, when PETRA gains STR consumption:

```text
petra -> tensor_view -> shapes
```

SHAPES must not depend on:

```text
tensor_view
petra
future interpretation packages
```

Tensor View must not depend on:

```text
petra
COLLATZ
future semantic interpretation packages
```

Thus:

```text
SHAPES -X-> Tensor View
SHAPES -X-> PETRA
Tensor View -X-> PETRA
```

The package boundary mirrors the promoted conceptual architecture.

---

## 4. STR runtime value object

The first runtime representation will be an immutable value object:

```python
@dataclass(frozen=True, slots=True)
class STR:
    root: int
    multiplicities: tuple[tuple[int, ...], ...]
```

Conceptually:

```text
root
    local coordinate selecting the complete input structural type

multiplicities[i][j]
    multiplicity of child structural type j
    under parent structural type i
```

The Python object is one deterministic representative of the mathematical STR
equivalence class modulo simultaneous coordinate renaming.

Coordinate numbers are representation metadata.

They are not:

- persistent structural-type identity;
- SHAPES ontology;
- occurrence identity;
- semantic labels;
- stable IDs across independently evolving runtime representations.

---

## 5. Primary construction API

The initial public Tensor View operation will be:

```python
def materialize(shape: Shape) -> STR:
    ...
```

Conceptually:

```text
Shape
    ↓ materialize
STR
```

`materialize()` owns:

- discovery of distinct rooted structural subform types;
- quotient construction;
- child multiplicity extraction;
- deterministic coordinate assignment;
- root-coordinate selection;
- construction of the immutable STR value.

The implementation must not mutate the input `Shape`.

---

## 6. Canonical runtime representative

The mathematical STR object is invariant under coordinate renaming.

The runtime nevertheless needs deterministic equality, hashing, tests, and
debugging.

Therefore `materialize()` must produce a canonical local-coordinate
representative.

For structurally equal input forms:

```python
materialize(left) == materialize(right)
```

must hold.

Repeated materialization of the same structural form must be deterministic.

This does not promote coordinate numbers into intrinsic identity.

Canonical coordinates are runtime representation details only.

---

## 7. Independence from Shape private representation

Tensor View must not make `Shape._key` part of its public contract.

The current SHAPES runtime uses `_key` as an internal canonical structural
representation detail.

Tensor View may inspect public SHAPES structure:

```text
Shape.children
structural equality
child multiplicity
```

but the STR contract must remain valid if SHAPES later changes its private
canonical-key implementation.

Therefore:

```text
Shape._key
```

must not appear in:

- public Tensor View APIs;
- STR serialized meaning;
- STR identity documentation;
- interpretation semantics.

An implementation may use private helpers only if explicitly justified and
replaceable without altering STR semantics.

The preferred implementation derives its own structural signatures from the
public recursive structure.

---

## 8. STR invariants

Every runtime `STR` produced by `materialize()` must satisfy:

```text
STR_COORDINATE_SET_NONEMPTY=YES

STR_ROOT_COORDINATE_VALID=YES

STR_MATRIX_SQUARE=YES

STR_MULTIPLICITIES_NONNEGATIVE_INTEGERS=YES

STR_DEPENDENCY_GRAPH_FINITE=YES

STR_DEPENDENCY_GRAPH_ACYCLIC=YES

STR_ALL_COORDINATES_ROOT_REACHABLE=YES

STR_DISTINCT_COORDINATES_DENOTE_DISTINCT_STRUCTURAL_TYPES=YES

STR_CANONICAL_COORDINATE_ORDER_DETERMINISTIC=YES
```

The zero-child SHAPES form therefore materializes to one coordinate with a zero
row.

---

## 9. Construction authority

In the first runtime milestone, the supported construction path is:

```text
Shape -> materialize() -> STR
```

M1 does not require a public arbitrary raw constructor contract such as:

```python
STR(root=..., multiplicities=...)
```

for user-supplied matrices.

The dataclass initializer may exist mechanically, but arbitrary externally
constructed values are not yet promised as accepted semantic inputs unless
explicit validation is introduced.

A future API may add:

```python
STR.from_raw(...)
```

or an equivalent validated constructor.

That decision is deferred.

---

## 10. Validation model

Two different validation concerns must remain separate.

### SHAPES validation

```python
shapes.validate(shape)
```

validates SHAPES runtime state.

### STR validation

STR validation concerns representation invariants such as:

- root range;
- matrix shape;
- multiplicity type/domain;
- acyclicity;
- root reachability;
- quotient-type uniqueness;
- deterministic representative constraints.

M1 should validate all values produced by `materialize()` through construction
logic and focused tests.

A public:

```python
validate_str(...)
```

function is not required in M1 unless implementation pressure demonstrates a
real consumer need.

---

## 11. Stack safety

Python recursion depth must not become part of STR semantics.

SHAPES already supports deep unary structures beyond ordinary Python recursion
limits.

Therefore Tensor View must preserve this engineering property.

At minimum:

```text
deep unary depth = 2048
```

must materialize without `RecursionError`.

The preferred implementation strategy is iterative:

```text
discover structural types
    ↓
build dependency information
    ↓
bottom-up structural signatures
    ↓
canonical coordinate assignment
    ↓
construct multiplicity matrix
```

Recursive mathematical definitions do not imply recursive Python call stacks.

---

## 12. Equality and hashing

`STR` is an immutable value object.

For canonical representatives:

```python
left == right
```

means equality of:

```text
root
multiplicities
```

because coordinate canonicalization has already normalized representation
choice.

Therefore the frozen dataclass may use ordinary value equality and hashing.

This runtime convenience does not redefine mathematical STR equivalence.

The mathematical equivalence remains coordinate-renaming invariant.

---

## 13. No public decoder in M1

The mathematical research proves STR faithfulness and defines a conceptual
decoder.

M1 does not automatically expose:

```python
decode(str_value) -> Shape
```

as public API.

Faithfulness can be tested without committing to a public reverse contract.

Possible test mechanisms include:

- independent structural signatures;
- bounded exhaustive comparison;
- private test helpers;
- cross-checks against known materialization examples.

A public decoder requires a separate API decision.

---

## 14. LAMBDA runtime ownership

LAMBDA is an architectural contract:

```text
Λ_I : STR -> D_I
```

It is not initially a shared Python base class.

M0 explicitly rejects premature introduction of:

```python
class LambdaBase:
    ...
```

or a generic interpretation registry.

Each interpretation owns its own STR-facing operation.

For example:

```python
LRPE.interpret_str(str_value: STR) -> int
```

and a future COLLATZ runtime could own:

```python
interpret_str(str_value: STR) -> int
```

inside its own package.

A shared Python `Protocol` may be introduced only after at least two maintained
runtime implementations demonstrate a stable common surface.

---

## 15. PETRA migration policy

The existing PETRA contract remains valid:

```python
LRPE.interpret(shape)
```

The first STR-facing PETRA extension should be additive:

```python
LRPE.interpret_str(str_value)
```

with the required equivalence:

```text
LRPE.interpret(S)
=
LRPE.interpret_str(materialize(S))
```

for every supported SHAPES form under equivalent explicit runtime limits.

M0 does not authorize replacing:

```text
Shape -> LRPE
```

with:

```text
Shape -> materialize -> LRPE
```

internally.

That migration requires a separate decision after runtime equivalence has been
demonstrated.

---

## 16. COLLATZ runtime policy

COLLATZ has validated the boundary as research.

Its proved structural seed is:

```text
χ(Z) = 1

χ(U)
=
1
+
Σ_T mult_U(T) * (χ(T) + 1)^2
```

and:

```text
χ = Λ_COLLATZ ∘ C.
```

COLLATZ is useful as a second runtime consumer after the Tensor View and PETRA
STR paths are stable.

It should not be introduced in M1.

When introduced, STR must still contain no:

- parity field;
- Collatz transition state;
- trajectory;
- COLLATZ-specific cache;
- semantic seed field.

Those remain interpretation-owned data.

---

## 17. Failure model

M1 should distinguish programmer/API misuse from impossible internal state.

Expected input-domain failures include:

```text
non-Shape materialize input
```

which should fail consistently with the existing SHAPES validation model.

Internal representation invariant failures indicate implementation defects.

M1 should not introduce broad exception hierarchies without demonstrated need.

Future raw STR ingestion, parsing, or serialization may require explicit
representation-domain exceptions.

That is deferred.

---

## 18. Public API candidate for M1

The intended minimal public package surface is:

```python
from tensor_view import STR, materialize
```

and:

```python
__all__ = [
    "STR",
    "materialize",
]
```

Nothing else is required initially.

In particular, M1 does not require public exposure of:

- structural signature helpers;
- graph traversal helpers;
- coordinate-renaming helpers;
- raw validators;
- decoder functions;
- serialization helpers;
- caches;
- incremental update machinery.

---

## 19. Packaging consequences

When M1 begins, `pyproject.toml` will need to include:

```text
tensor_view
```

alongside:

```text
shapes
petra
```

and static analysis configuration must include the new runtime package.

Those are implementation changes and therefore are intentionally absent from
M0.

---

## 20. Required M1 tests

The first Tensor View implementation must include focused tests for at least:

### Zero form

```text
Z
```

materializes to a single structural type with no child dependencies.

### Multiplicity

Repeated equal children produce one child structural-type coordinate with the
full intrinsic multiplicity.

### Sibling permutation

Structurally equal forms built with different input sibling order produce equal
STR values.

### Structural equality

Equal SHAPES values produce equal STR values.

### Structural distinction

Distinct SHAPES forms produce distinct STR values.

This requirement follows from proved STR faithfulness, not from any LAMBDA
interpretation.

### Quotient sharing

Repeated equal rooted subforms occupy one structural-type coordinate.

### Root reachability

Every coordinate in a materialized STR is reachable from the root coordinate.

### Acyclicity

The dependency graph is acyclic.

### Determinism

Repeated materialization yields identical canonical representatives.

### Deep stack safety

A unary SHAPES form of depth 2048 materializes without `RecursionError`.

### Bounded exhaustive conformance

A complete bounded SHAPES corpus must confirm:

```text
equal Shape -> equal STR
distinct Shape -> distinct STR
all STR invariants hold
```

The bound should be proportionate to runtime-test cost and need not reproduce
the full research corpus on every default CI run.

---

## 21. Deferred capabilities

The first implementation explicitly defers:

```text
incremental STR maintenance

ADD directly on STR

REMOVE directly on STR

public STR decoder

serialization format

parser

persistent coordinate IDs

coordinate-stability guarantees across edits

runtime caching contract

Operational History integration

generic LAMBDA base class

interpretation registry

plugin framework

mandatory STR interpretation path

automatic PETRA runtime migration

COLLATZ production package
```

These require independent evidence or consumer demand.

---

## 22. Milestones

### M0 — Runtime design

Status:

```text
DESIGN_ONLY
```

Deliver:

- package ownership;
- minimal API;
- STR invariants;
- canonical-coordinate policy;
- stack-safety requirement;
- LAMBDA ownership rule;
- migration boundaries;
- test contract.

No runtime code.

### M1 — Tensor View runtime

Introduce:

```text
src/tensor_view/
    __init__.py
    core.py
    py.typed
```

with:

```python
STR
materialize
```

and focused tests.

Update packaging and static-analysis scope.

### M2 — Tensor View conformance

Strengthen evidence with:

- bounded exhaustive corpus;
- faithfulness checks;
- invariant checks;
- deep-structure tests;
- deterministic materialization checks.

No interpretation migration.

### M3 — PETRA STR consumer

Add an explicit PETRA-owned:

```python
LRPE.interpret_str(...)
```

implementing the proved:

```text
Λ_LRPE : STR -> N+
```

No change yet to existing `LRPE.interpret(shape)` internals.

### M4 — PETRA equivalence gate

Establish runtime equivalence:

```text
LRPE.interpret(S)
=
LRPE.interpret_str(materialize(S))
```

including equivalent runtime-limit behavior.

Only after this gate may an internal PETRA migration be considered.

### M5 — second runtime interpretation

Introduce a maintained COLLATZ runtime consumer only if still useful.

It must implement the already proved STR-owned boundary without adding COLLATZ
semantics to STR.

### M6 — shared LAMBDA interface decision

Status:

```text
DONE
```

After M5, two maintained STR consumers exist with real runtime surfaces:

```python
LRPE.interpret_str(
    value: STR,
    *,
    limits: MaterializationLimits | None = None,
) -> int
```

and:

```python
collatz.interpret_str(value: STR) -> int
```

Their proven architectural commonality is:

```text
STR input
    ↓
interpretation-owned LAMBDA
    ↓
interpretation domain
```

Their runtime surfaces are intentionally not identical.

PETRA/LRPE owns:

- policy identity;
- optional materialization limits;
- direct SHAPES interpretation;
- reverse interpretation;
- PETRA-specific runtime failures.

COLLATZ currently owns only:

```text
STR -> structural seed
```

and has no demonstrated requirement for PETRA-style materialization limits,
reverse interpretation, policy identity, or a policy object.

No maintained runtime caller currently needs to accept arbitrary LAMBDA
implementations polymorphically.

Introducing a shared `Protocol`, base class, registry, adapter, or wrapper now
would therefore encode abstraction before there is a demonstrated consumer for
that abstraction.

The M6 decision is:

```text
NO_SHARED_PROTOCOL_REQUIRED
```

This decision does not deny the architectural LAMBDA contract:

```text
Λ_I : STR -> D_I
```

It means only that the architectural contract does not currently justify a
shared Python runtime interface.

Each interpretation continues to own its STR-facing API.

The decision should be reconsidered only if concrete runtime pressure appears,
for example:

- a maintained caller must accept multiple STR interpreters interchangeably;
- a third maintained interpreter exposes a stable compatible surface;
- interpretation discovery or registration becomes a real requirement;
- a shared failure or resource-limit contract emerges independently across
  interpreters.

Until then:

```text
INTERPRETER_OWNS_ITS_LAMBDA=YES
GENERIC_LAMBDA_BASE_CLASS=NO
SHARED_LAMBDA_PROTOCOL=NO
INTERPRETATION_REGISTRY=NO
RUNTIME_CHANGE_M6=NONE
```

---

## 23. Dependency target

The intended runtime graph after M5 is:

```text
                    shapes
                      ↑
                      │
                 tensor_view
                  ↑       ↑
                  │       │
               petra    collatz
```

Direct interpretation remains allowed by architecture.

Therefore this graph may coexist with:

```text
petra -> shapes
```

during migration.

No circular dependency is permitted.

---

## 24. Design invariants

The runtime design commits to:

```text
SHAPES_REMAINS_INTERPRETATION_AGNOSTIC=YES

TENSOR_VIEW_IS_SEPARATE_PACKAGE=YES

STR_IS_IMMUTABLE_VALUE_OBJECT=YES

STR_COORDINATES_ARE_METADATA=YES

STR_CANONICAL_RUNTIME_REPRESENTATIVE=YES

STR_PUBLIC_IDENTITY_DOES_NOT_DEPEND_ON_SHAPE_PRIVATE_KEY=YES

MATERIALIZE_IS_PRIMARY_M1_CONSTRUCTOR=YES

PUBLIC_RAW_STR_INGESTION_M1=NO

PUBLIC_DECODER_M1=NO

STACK_SAFE_MATERIALIZATION_REQUIRED=YES

GENERIC_LAMBDA_BASE_CLASS_M1=NO

INTERPRETER_OWNS_ITS_LAMBDA=YES

PETRA_DIRECT_SHAPE_API_PRESERVED=YES

PETRA_INTERNAL_STR_MIGRATION_M0=NO

COLLATZ_RUNTIME_M1=NO

OPERATIONAL_HISTORY_IN_STR=NO

RUNTIME_CHANGE_M0=NONE
```

---

## 25. M0 decision

The runtime implementation may proceed to M1 only under this boundary:

```text
Shape
    ↓
tensor_view.materialize
    ↓
immutable canonical STR
```

with interpretation semantics strictly above STR.

The first implementation must stay deliberately small.

The objective is not to build a tensor framework.

The objective is to implement exactly the already-proved structural
representation boundary with the smallest stable runtime surface.
