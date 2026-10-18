# COLLATZ Interpretation v0.1.0

Release status: candidate — not yet published.

## Summary

Initial independent distribution of the historical COLLATZ
structural seed interpretation over ASHES Tensor View / STR.

## Scope

The maintained operation `interpret_str` evaluates the structural
seed recursively. It is not the Collatz 3n+1 iteration.

No claim is made that the mapping is injective or that the
Collatz conjecture is proved.

The historical implementation has been recovered without
runtime semantic changes.

## Package

- Distribution: `collatz-interpretation`
- Version: `0.1.0`
- Proposed Git tag: `collatz-v0.1.0`
- Python: `>=3.10`
- Dependency: `agnostic-shapes-core>=4.0.0,<5.0.0`
- No PETRA dependency

## Verification

Six historical tests passed. Wheel and sdist boundaries were
verified. Installation with published ASHES 4.0.0 succeeded
offline in a clean environment.

## Publication boundaries

PyPI publication has not been established.

No COLLATZ Zenodo DOI is assigned in this candidate.

Historical release provenance remains unchanged.
