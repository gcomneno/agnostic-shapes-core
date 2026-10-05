# Resolver

Resolver is a satellite package over the SHAPES structural core.

During the SHAPES/PETRA separation, the maintained structure-only runtime is
exposed through explicit submodules rather than through the `resolver` package
root:

```python
from resolver.shapes_search import resolve_shapes
from resolver.shapes_distance import structural_distance_shapes
from resolver.shapes_verify import verify_shapes_path
```

The dependency chain is:

```text
resolver.shapes_verify
        ↓
resolver.shapes_distance
        ↓
resolver.shapes_search
        ↓
      SHAPES
```

These modules operate on `shapes.Shape`, intrinsic `ADD` / `REMOVE`, and
state-scoped `OccurrencePath` selectors.

The package root intentionally exports no compatibility API.

## Migration status

Pre-separation PETRA-coupled Resolver modules still exist temporarily while the
repository completes the architectural migration. The classic search,
distance, and verification runtime and its dependent atlas, fingerprint,
notation, and structural-algebra surfaces have been retired.

The projection layer and the remaining structural-deconstruction research
surface remain temporarily for later Phase 3 admission or retirement.

Those modules are compatibility or research artifacts. Their presence does not
make their semantics part of SHAPES, and they are scheduled for retirement or
quarantine before the old structural `petra` package is removed.

The retired classic search, distance, and verification APIs are not aliases for
the SHAPES-native APIs.

Remaining legacy names such as `PrimeKey`, `project`, `contains`, `meet`, and
`join` are likewise not re-exported from `resolver`.

## Command line

The pre-separation Resolver command-line programs have been retired during
Phase 2.4.

The package currently installs no Resolver CLI entry points.

No replacement SHAPES CLI, parser, serializer, or schema has been admitted yet.

A period with no Resolver CLI is intentional and preferable to promoting the
legacy PETRA representation into SHAPES.

## Phase 3 boundary

Integer conversion, factorization, prime assignment, numeric projection, and
related interpretation behavior are not SHAPES responsibilities.

No executable compatibility placeholder is required for them during Phase 2.
Any future PETRA interpretation functionality will be introduced later from an
explicit Phase 3 contract over SHAPES.
