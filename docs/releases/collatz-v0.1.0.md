# COLLATZ Interpretation v0.1.0

Release status: historical release candidate, retired from the active programme.

The package has been removed from the maintained tree. The candidate details
and verification record below describe historical work, not current support
or newly executed checks. No publication, created Git tag, or DOI is established
by this retirement.

## Summary

Initial independent distribution of the historical COLLATZ
structural seed interpretation over ASHES Tensor View / STR.

## Scope

The then-maintained operation `interpret_str` evaluated the structural
seed recursively. It is not the Collatz 3n+1 iteration.

No claim is made that the mapping is injective or that the
Collatz conjecture is proved.

The historical implementation was recovered for this candidate without
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
