# ASHES / PETRA — Independent distribution release contract

Status: D3 preparation. Not a publication authorization.

## Distribution identities

### ASHES

- Python distribution: `agnostic-shapes-core`
- Candidate version: `4.0.0`
- Runtime packages: `shapes`, `tensor_view`
- Semantics: governed by `docs/reference/SPEC.md`
- Dependency on PETRA: forbidden

Version 4.0.0 changes the historical distribution boundary by removing
PETRA and COLLATZ from the ASHES wheel and source distribution.

### PETRA

- Python distribution: `petra-interpretation`
- Candidate version: `0.1.0`
- Runtime package: `petra`
- Dependency: `agnostic-shapes-core>=4.0.0,<5.0.0`
- Normative reference: `docs/reference/PETRA.md`

PETRA's candidate version is not yet a historical publication claim.

## Publication order

1. Freeze distribution versions and dependency contracts.
2. Prepare separate citation and release metadata.
3. Validate the release artifacts against the frozen metadata.
4. Publish ASHES independently.
5. Verify the published ASHES artifact and its dependency identity.
6. Publish PETRA against the published ASHES distribution.
7. Reconcile GitHub releases with their respective Zenodo records.

Each publication requires explicit approval.

## Bibliographic boundaries

- Preserve historical tags, releases, DOI records and attribution.
- ASHES historical v3.0.0 DOI: `10.5281/zenodo.23161216`.
- ASHES concept DOI: `10.5281/zenodo.23161215`.
- Historical PETRA derivation DOI: `10.5281/zenodo.22741778`.
- Do not reuse a version DOI as the DOI of another release.
- Do not invent or preassign Zenodo record identifiers.
- Do not claim PETRA's standalone DOI exists before deposit.
- Reconcile `CITATION.cff` only with verified release metadata.

## Release gates

- Distribution name and version: explicit and unique.
- Wheel and sdist: isolated, reproducibly buildable.
- Runtime dependency: installable from intended published artifacts.
- GitHub CI: successful on the release commit.
- Citation metadata: consistent with the target release.
- Release notes: explain compatibility and historical provenance.
- Git tag: absent until authorization.
- GitHub Release: absent until authorization.
- Zenodo deposit: absent until authorization.

A passing CI run alone does not authorize a release.
