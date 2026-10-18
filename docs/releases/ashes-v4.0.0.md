# ASHES v4.0.0

Release status: candidate — not yet published.

## Summary

ASHES is now distributed independently as the agnostic SHAPES
structural core, including its neutral tensor/STR representation.

## Compatibility

This is a breaking distribution change relative to v3.0.0.

The ASHES distribution contains only the `shapes` and
`tensor_view` runtime packages.

The `petra` and `collatz` runtime packages are no longer included.
PETRA is maintained as a separate distribution; COLLATZ is not
part of the maintained runtime.

## Package

- Distribution: `agnostic-shapes-core`
- Version: `4.0.0`
- Proposed Git tag: `v4.0.0`
- Python: `>=3.10`

## Verification

Wheel and sdist isolation, clean installation, maintained tests,
static checks, documentation checks, and GitHub CI have passed
during the distribution-separation work.

## Publication boundaries

PyPI publication has not been established.

No new Zenodo version DOI is assigned in this candidate.

Historical release tags, metadata and DOI records remain unchanged.
