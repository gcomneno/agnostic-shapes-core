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

The pre-separation PETRA-coupled Resolver runtime has been retired.

The maintained Resolver runtime is now limited to the explicit SHAPES-native
submodules:

```text
resolver.shapes_search
resolver.shapes_distance
resolver.shapes_verify
```

The package root exports no compatibility API, and no legacy projection,
structural-deconstruction, numeric, or classic Resolver runtime remains
installed.

Historical PETRA research remains preserved in repository history and research
material; it is not retained as executable compatibility code.

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
