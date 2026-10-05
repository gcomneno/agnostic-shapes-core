# PETRA Documentation

## Read this first

1. [Canonical SHAPES specification](reference/SPEC.md)
2. [PETRA interpretation specification](reference/PETRA.md)
3. [SHAPES / PETRA vision](VISION.md)
4. [Implementation roadmap](../ROADMAP.md)
5. [Current status](reports/STATUS.md)

The specification is the only normative source.

## Active documentation

- `reference/SPEC.md` — canonical SHAPES carrier, intrinsic edits,
  representation boundary, and SHAPES conformance.
- `reference/PETRA.md` — normative PETRA prime/exponent interpretation
  contract, including the PIP boundary.
- `VISION.md` — project purpose and architectural direction.
- `../ROADMAP.md` — dependency-ordered implementation plan.
- `reports/STATUS.md` — current transition status.

## Historical and research material

The repository still contains documents produced during PET, PET/PEG 2.0,
and PET-Metrics development.

They are retained temporarily for provenance and migration analysis. Unless the
canonical PETRA specification explicitly incorporates a rule, those documents
are:

- historical;
- superseded;
- research-only;
- non-normative.

Directory indexes state the classification of their contents.

## Source-of-truth rule

When structural material conflicts with `reference/SPEC.md`, the SHAPES
specification wins. When PETRA interpretation material conflicts with
`reference/PETRA.md`, the PETRA interpretation specification wins.

No old CLI, JSON, operator, trace, graph, metric, or compatibility statement is
binding on PETRA merely because it was previously stable.
