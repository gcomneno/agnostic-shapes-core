# Agnostic SHAPES Core v3.0.0

Agnostic SHAPES Core v3.0.0 is the first release under the ASHES project
identity.

It freezes the architectural separation completed after PETRA v2.1.0:

```text
PETRA -> SHAPES

SHAPES -X-> PETRA
```

SHAPES is now the maintained interpretation-agnostic structural core.
PETRA is a pluggable prime/exponent interpretation layer over SHAPES.

## SHAPES

The maintained `shapes` package provides:

- `Shape`
- `OccurrencePath`
- `size`
- `add`
- `remove`
- `iter_occurrences`
- `validate`

SHAPES owns structural identity, intrinsic multiplicity, sibling non-order,
occurrence-local targeting, intrinsic size, and elementary `ADD` / `REMOVE`
structure.

Prime assignment, exponent semantics, factorization, and represented integer
values are not SHAPES semantics.

## PETRA

The maintained `petra` package is now an interpretation layer over SHAPES.

LRPE — Local-Rank Paired-Exponent — is the first maintained executable PETRA
policy.

Its public runtime exposes:

- `LRPE`
- `LRPEPolicy`
- `MaterializationLimits`
- `MaterializationLimitError`
- `ReverseDomainError`

LRPE is faithful, has a proper decidable image, and provides an effective
inverse on that image under the maintained PETRA contract.

PETRA remains broader than LRPE.

## Resolver

Resolver remains a separately packaged satellite over SHAPES.

Its maintained structural modules are:

- `resolver.shapes_search`
- `resolver.shapes_distance`
- `resolver.shapes_verify`

Resolver is not part of SHAPES ontology.

## Breaking changes

v3.0.0 is not backward compatible with PETRA v2.1.0.

The pre-separation structural PETRA runtime has been retired, including its
CLI, serialization, schemas, positional addresses, typed structural model,
metrics, result/witness envelopes, and named structural compatibility
operators.

Consumers should use `shapes` for maintained structural behavior and explicit
PETRA interpretation APIs for maintained prime/exponent interpretation.

## Historical continuity

Historical PET and PETRA releases remain unchanged.

In particular, PETRA v2.1.0 remains the historical release associated with
Version DOI:

`10.5281/zenodo.23123734`

This DOI is not reused by ASHES v3.0.0.

Zenodo archived ASHES v3.0.0 in a distinct ASHES concept family.

ASHES Concept DOI:

`10.5281/zenodo.23161215`

ASHES v3.0.0 Version DOI:

`10.5281/zenodo.23161216`

The historical PET/PETRA Concept DOI remains:

`10.5281/zenodo.22741778`

ASHES is architecturally derived from that historical lineage, but its Zenodo
version family is distinct.
