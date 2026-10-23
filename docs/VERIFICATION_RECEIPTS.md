# Local verification receipt v1

`aec_cad.py check SPEC OUT` preserves the CLI and the report's existing `standard`, `errors`, `warnings` and `checked` fields. The result is a **supported-plan local check**, not a complete architectural package release or native acceptance. Every check invocation that reaches validation retains `OUT/receipts/<receipt_id>.json` and updates `OUT/check-report.json` with identical bytes. The receipt directory is append-only by this checker, not a tamper-proof or signed store.

| Field | Type and meaning |
| --- | --- |
| `schema_version` | String constant `gridline-check-receipt.v1` |
| `receipt_id`, `timestamp` | Unique run ID and UTC time |
| `status`, `return_code` | `PASS`/0 for attempted supported checks without errors; `FAIL`/1 otherwise |
| `code_sha` | Tracked repository HEAD SHA, or `UNKNOWN` in standalone installations |
| `validator_worktree_dirty` | Boolean, or null if Git provenance is unavailable; actual validator hashes remain authoritative for the checked implementation |
| `validator` | Name, Python version, dependency versions and SHA-256 map of validator scripts and building-contract schema |
| `ruleset_id`, `standard` | Versioned local rule identifier and selected effective standards-profile name |
| `input_hashes` | File path → SHA-256 of exact parsed spec/profile bytes, including inherited profiles; null when unavailable/over limit |
| `output_directory`, `output_hashes` | Output location and filename → SHA-256 of exact consumed artifact snapshots; null for missing/over-limit files |
| `artifact_manifest_hash` | SHA-256 of UTF-8 JSON of `output_hashes`, with sorted keys and compact separators |
| `coverage` | Named gate → status, scope and evidence; per-sheet geometry includes element IDs, DXF handles, inferred/XDATA association and primitive counts |
| `unverified_items` | Human-readable array of remaining coverage limits |
| `native_host_verified` | False for this local checker |
| `architect_review_status`, `operator` | `NOT_RUN` and `UNKNOWN`; user identity or architect approval is not inferred |
| `evidence_file_paths` | Paths to the inspected drawing/schedule artifacts |

Gate outcomes use `PASS`, `FAIL`, `NOT_RUN` and `UNKNOWN`. Mixed attempted/unavailable sheet checks aggregate to `UNKNOWN`; any measured failure aggregates to `FAIL`. Missing mandatory PDF validation blocks the overall result even though the unavailable validator gate remains `NOT_RUN`. Unsupported checks never become green simply because supported checks passed.

The checker reads each input once into a bounded snapshot and parses/hashes those same bytes: spec/profiles ≤10 MiB each, output artifacts ≤64 MiB each. It checks consumed snapshots against files again at receipt time and fails if any changed. This is not an atomic snapshot of multiple files, nor hardened MCP confinement. Source/outputs can change after checking; compare hashes before using a receipt. Non-atomic rebuilds and stale receipts remain a separate publication gate. A null hash never means an empty file or a successful inspection.

The drawing contract is [building-spec.v1.schema.json](../skills/architectural-drawing-generation/references/building-spec.v1.schema.json). Runtime shape, numeric and relational validation enforce explicit millimetres, finite numbers (booleans/text are not dimensions), level dimensions, references, IDs, spans and opening fit. The schema is an interchange description, not a regulatory validator; runtime additionally applies the chosen office profile. Legacy specs can omit the version marker. Unknown extra attributes are retained in the hashed source, but the generator does not automatically implement or verify them.

Geometry tolerances (0.01 mm and PDF 0.05 point) are local numerical comparison tolerances, **not office-approved construction tolerances**. DXF wall joins follow this generator's documented half-thickness extension within 1 mm of another wall's centerline. Topological correctness, wall construction, source-detail completeness, dimensions/hatches/grids, PDF raster visibility/clipping/fonts, native identity persistence, 3D/rendering, IFC/IDS and professional approval are separately unverified.

PDF parsing uses the [pypdf visitor API](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) to measure straight vector segments. This parser is scoped to the generated PDFs; it does not promise arbitrary external PDF geometry extraction. Document metadata strengthens identity but is not geometric evidence. Legacy missing metadata is explicitly `UNKNOWN`. New DXF associations use [extended data](https://ezdxf.readthedocs.io/en/stable/dxfinternals/dxftags.html#extended-data), whose survival through a native roundtrip remains untested.
