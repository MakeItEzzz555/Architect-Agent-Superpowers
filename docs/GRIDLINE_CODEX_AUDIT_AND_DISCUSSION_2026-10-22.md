# Gridline: independent technical audit and design discussion

Date: 2026-10-22. Reviewed baseline: `a1c7797e151edde8cf6e8d76807da901de708bf2`, version 0.7.0, branch `docs/codex-technical-audit-20261022`. Scope: the isolated checkout only. This is one Codex agent's independent review of the implementation, not an independent professional certification or a multi-reviewer assessment.

## Executive summary

What this repo does: Gridline packages 30 portable AEC workflow skills, provider adapters, conceptual SVG/DXF generation, a coordinated plan-sheet generator/checker, and a read-only JSON revision-impact pilot. The assumed workload is a small practice reviewing one project with occasional concurrent filesystem/model activity, not a hosted multi-tenant service.

The strongest near-term product is **evidence-backed coordination review of existing drawings**, with a named architect resolving findings. Professional AutoCAD-ready drawing-set claims are premature: no native roundtrip was demonstrated, sections/elevations/details are unimplemented, and the checker does not establish actual geometric agreement or PDF quality. The README and next-phase documentation already acknowledge many limitations, but some drawing-check descriptions overstate what is measured.

The most consequential findings are checker blind spots, missed revision dependencies, and non-atomic output publication. A demonstrated filesystem race weakens the otherwise sensible MCP confinement. There is no current native-write implementation to accuse of corrupting a building model; its missing transaction manager is a **release blocker for future writes**, not evidence of an existing write vulnerability.

Local validation discovered 41 unit tests: **30 passed, 11 skipped**. All coordinated CAD tests were skipped because dependencies were absent. Structural activation fixtures do not demonstrate real model behavior. Prioritize #15 state safety before writes, while proving #10 cross-sheet review and #16 AutoCAD compatibility. Implement #11 IFC/IDS validation before advertising BIM exchange quality; it need not delay a clearly bounded DXF review MVP.

## Evidence and implementation matrix

Paths below are repository-relative. For compact citations, `S/` means `skills/architectural-drawing-generation/scripts/`; `R/` means that skill's `references/`. Line references refer to the reviewed SHA.

| Capability | Factual status | Implementation and evidence |
|---|---|---|
| Thirty skill descriptions, portable packaging, provider-copy consistency | Implemented + locally tested structurally | `skills/*/SKILL.md`, `skills/manifest.json`, `tests/check_repo.py`, `scripts/sync-provider-skills.py`; all 30 descriptions inspected. This proves packaging, not architectural competence. |
| Six conceptual primitives to SVG/ASCII DXF | Implemented + locally tested | `S/aec_draw.py`; four tests in `tests/test_aec_draw.py`. String/file assertions and zero-length dimension rejection; no native CAD acceptance. |
| JSON changes, explicit sheet references, schedule review queue | Implemented + locally tested | `S/revision_impact.py`; 13 tests in `tests/test_revision_impact.py`. Partial reference coverage is explicitly returned. |
| Authorized-root MCP helper functions | Implemented + locally tested | `S/gridline_mcp.py:19–57`; seven tests in `tests/test_gridline_mcp.py`. Input bytes preserved; absolute/traversal/static symlink paths rejected. |
| Actual MCP transport, SDK registration and client session | Implemented but integration-unverified | `S/gridline_mcp.py:60–85`; SDK absent. Tests call helpers and missing-root startup, not an initialized STDIO client/server exchange. No CAD connection. |
| R2018 DXF plans, layouts, PDFs, four CSVs, standards profiles | Implemented but not host-tested; local CAD tests unavailable here | `S/aec_cad.py:217–505`, `R/standards/{iso13567,ncs}.json`; 11 tests in `tests/test_aec_cad.py`, all skipped locally. Source inspection is not a successful build receipt. |
| Drawing/check consistency | Implemented with significant limits | `S/aec_cad.py:515–682`; compares profile properties, title fields, viewport ratio, text/tag sets and CSV/spec values. Does not read PDFs or measure emitted wall/opening geometry. |
| External 40-sheet content comparison, PDF geometry QA | Documented only; extraction/checking unimplemented | `docs/NEXT_AEC_PHASES.md`, issue #10. Declared references do not inspect drawing contents. PDF header assertion at `tests/test_aec_cad.py:54` is not geometry QA. |
| IFC schema/EXPRESS + IDS release gate | Documented only; validator integration unimplemented | `skills/openbim-ifc-coordination/SKILL.md`, `docs/NEXT_AEC_PHASES.md`, #11. No IFC/IDS validator executable or fixture suite found. |
| Native hosts, transactional edits, coherent 3D, scan reconstruction | Documented only; Gridline adapters/pipelines unimplemented | `docs/TOOL_INTEGRATIONS.md`, `docs/NEXT_AEC_PHASES.md`, #12–#15. Skill guidance is not an installed adapter. |
| Mandatory code, permit, structural/fire/accessibility compliance | Not established by these tools | `AGENTS.md`, README professional boundary. IFC **structural data quality** means schema/relationships, not structural engineering safety. Geometry, IDS, permits and professional signing remain distinct gates. |

All of `README.md`, `ROADMAP.md`, the four requested technical docs, `AGENTS.md`, canonical drawing/revision/MCP scripts, their tests, `tests/check_repo.py`, both installers, sync/native-validation scripts and CI configuration were inspected. All skill descriptions were read; selected drawing/QA/openBIM skill bodies were read. Full specialist bodies, agent instructions, every reference/template, historical commits and all provider behavior were not audited exhaustively.

## Verified findings

Severity is impact within the stated workload. “Reproduced” means a local probe executed; “static” means a concrete code path was inspected without the unavailable CAD dependency.

### 1. High — checker success does not establish geometric or PDF agreement

**Evidence (static):** `S/aec_cad.py:596–606` compares opening ID text and room name/area text. `:621–663` recomputes expected schedules from the spec using the same area function as generation. It never measures emitted opening widths, wall positions or room boundary areas. No PDF is opened anywhere in `check`. The checker therefore cannot distinguish a correctly labeled plan from one with displaced wall geometry and unchanged tags. Removing a PDF also has no checker branch to detect it. `docs/DRAWING_OUTPUTS.md` describes stronger geometry agreement than this establishes.

**Smallest correction:** narrow the claim immediately; add targeted geometry readback for supported primitives with stable element associations, PDF existence/page/scale checks, and deliberate output-corruption tests. Keep visual review for collisions. Skipping this lets apparently green reports accompany incorrect deliverables. No native or dependency-backed corruption test was run here.

### 2. High — revision changes omit supported inputs and indirect dependencies

**Evidence (reproduced):** `S/revision_impact.py:19,107–140` compares levels/walls/openings/rooms, sheets and project fields, but not grids, units or the selected standards profile. Moving a grid or changing `standard` from `iso13567` to `ncs` returned `NO_INDEXED_CHANGES` on the example. `S/aec_cad.py:263–271` actually draws those grids.

`S/revision_impact.py:67–86` has direct references and level matching, not dependency traversal. With an existing A-301 referencing only opening W01 and no matching level, changing its host wall E1's thickness returned only A-101/A-102. Moving E1's level produced an empty `schedules_to_recheck`, although opening schedule `level` derives from the wall (`S/aec_cad.py:494`).

**Smallest correction:** compare every output-affecting input, invalidate broadly for units/profile changes, and traverse typed wall→opening→sheet/schedule dependencies. Add negative controls for unchanged unrelated elements. The existing PARTIAL warning is honest but does not repair missing dependencies inside the declared index.

### 3. Medium — path confinement has a check/open race

**Evidence (reproduced):** `S/gridline_mcp.py:28–35` resolves/stats a path, returns it, then `:44` calls `read_spec`; `S/revision_impact.py:47` reopens by pathname. After validation of `authorized/part/spec.json`, renaming `part` and replacing it with a symlink to a sibling directory made that read return a synthetic `OUTSIDE_SENTINEL` project. Only temporary test directories were involved.

This requires another process able to mutate an authorized ancestor directory; a caller supplying a static escape cannot bypass the tested checks. It is not evidence of remote shell execution. Replacing/growing a file after `stat` similarly undermines the size check and snapshot consistency.

**Smallest correction:** read bounded bytes from a securely opened descriptor, confine traversal against a pinned root using platform-supported no-follow/descriptor-relative operations, and parse/hash those same bytes. Define immutable-snapshot behavior where portable primitives differ. Test ancestor replacement and file growth. Do not describe the current pathname check as race-proof isolation.

### 4. High — failed rebuilds can leave a mixed output revision

**Evidence (static):** `S/aec_cad.py:472–501` overwrites DXF/PDF sheets sequentially, then CSVs. `:480–484` returns when a later sheet does not fit. On an existing output directory, an updated A-101 can therefore coexist with old A-102 and old schedules; removed sheets are not cleaned from the directory. `build` does not invalidate a previous `check-report.json` before starting. A failed invocation could leave a stale PASS file beside mixed artifacts.

**Smallest correction:** build into a fresh revision directory, validate the complete artifact inventory, then publish an explicit manifest/pointer atomically. Preserve the last approved set. Inject a second-sheet failure and verify no newly published mixed set. This concerns generated outputs, not a demonstrated native-model write.

### 5. Medium — validation accepts incomplete dimensional truth

**Evidence (reproduced):** deleting `units` from the example yielded no `aec_cad.validate` errors (`S/aec_cad.py:132` defaults to mm). Setting a level height to -1 also yielded no errors; levels are used for IDs at `:141` but lack height/elevation validation. The separate `R/aec-drawing.schema.json` describes conceptual primitives, not the building spec. Current opening checks enforce horizontal fit and positive opening dimensions, not complete vertical/topological constraints.

**Smallest correction:** explicitly require units and finite typed values; validate level dimensions and supported host relationships. Version the building contract and reject ambiguous dimensions instead of silently supplying units. Keep unsupported topology checks visibly UNKNOWN. These are input-trust gaps, not proof of regulatory noncompliance.

### 6. Medium — reports cannot bind a result to the inspected revision

**Evidence (static):** `S/revision_impact.py:142–156` returns schema version, changes and limits, without input hashes/project identity/tool version. `S/aec_cad.py:675–676` overwrites its report without spec/profile/artifact digests. A same-name input replacement cannot be detected from the report. Sheet register comparison omits the generated date column (`:499–501` versus `:667–668`), so a stale register date is unexamined even though title dates are checked.

**Smallest correction:** include content digests, versions, coverage and explicit per-gate outcomes; compare date too. Write durable receipts separately from mutable working reports. Otherwise reviewers cannot prove which inputs a green result covered.

### 7. Medium — the green suite leaves transport, model behavior and CAD gates uncovered

**Evidence:** `tests/test_aec_cad.py:24` skips the entire class without ezdxf. MCP tests at `tests/test_gridline_mcp.py:67–73` only exercise startup without a root; no successful server/client handshake is tested. `tests/check_repo.py:107–131` counts activation fixtures, not activations. CI installs CAD dependencies in `.github/workflows/ci.yml`, but that file is not a final-head CI result. `docs/EVALS.md` correctly separates structural from behavioral evaluation.

**Smallest correction:** report attempted/pass/fail/skipped per capability; require an actual MCP contract session for integration releases. Run budget-approved behavioral evaluations separately. No claim of measured agent reliability, token savings or native compatibility follows from today's test count.

### 8. Low — conceptual render validation differs from its schema

**Evidence (reproduced):** negative circle radius renders as `r="-1"`; `S/aec_draw.py:118–123` checks finiteness only, while `R/aec-drawing.schema.json` requires positive radius. `--validate-only` renders instead of applying that schema (`S/aec_draw.py:260–268`).

**Smallest correction:** enforce the documented positive bounds in the existing numeric validation path and add one regression. Otherwise VALID can describe unusable SVG. This does not justify expanding the conceptual engine into a CAD kernel.

## Community feedback and product strategy

Issues #10–#16 were fetched through the read-only GitHub connector; all were open and unassigned at retrieval. Their recorded feedback is distinct from this audit's analysis. There were zero comments reported on those issues; the quotations below are preserved in issue bodies, not independently retrieved original discussion threads.

| Issue / actual feedback | Codex response and practical gate |
|---|---|
| [#15](https://github.com/MakeItEzzz555/Gridline/issues/15), recorded quotation: “make sure u handle teh state management well since architecture logic gets wierd fast when agents start hallucinating designs” | Agree: persistent state, deterministic validation and one commit authority must exist outside chat. Treat this as the prerequisite for writes. |
| [#16](https://github.com/MakeItEzzz555/Gridline/issues/16), recorded quotation: “The dxf generation part is what caught my eye ... how clean are they when you bring them into autocad” | Answer with native open/audit/edit/save/plot receipts, not another generated image or ezdxf audit. |
| [#10](https://github.com/MakeItEzzz555/Gridline/issues/10), recorded scenario: window change across approximately 40 sheets | Build a consented sheet inventory and independent reference truth. Distinguish “affected” from “verified updated.” |
| [#14](https://github.com/MakeItEzzz555/Gridline/issues/14), recorded scenario: erasures, artifacts, overlays, hand markup | Preserve conflicting hypotheses and image coordinates; abstain when unscaled; require reviewed 2D before 3D. |

My commercial hypothesis—not a willingness-to-pay study—is that small practices buy fewer missed revisions, reliable schedules, office-standard outputs, and evidence they can review quickly. Thirty broad skills help discovery; they do not themselves establish a defensible production advantage. Interview practicing architects and CAD technicians about their last failed issue, correction time and acceptable review burden before building more hosts.

An optional Gridline-owned read-only adapter gives users stable IDs, explicit coverage, bounded resource use and consistent receipts while retaining their chosen authoring software. Its objection is maintenance and potentially duplicating vendor tools. Keep it thin: normalize evidence and enforce authority, rather than recreating a modeling kernel. Native APIs offer transaction/identity access but require host-specific development. Vendor MCP reduces integration work but exposes only documented tools and evolving preview contracts. A custom local bridge can fill a necessary gap but creates an owned security/update surface. APS offers batch scale with cloud permissions, data transfer and billing consequences; it should be optional.

Choose **AutoCAD on a licensed Windows pilot machine** for the first live acceptance exercise: it tests the current DXF promise in #16 and can improve #10 without autonomous writes. A technician operates copies manually; this is not a new agent-write adapter. If that access cannot be secured, publish NOT TESTED and recruit a host owner. Revit Read is the first candidate for a subsequent live external MCP query pilot, once a 2027.2 partner is available. Do not start seven adapters concurrently.

## Executable authority and integration architecture

The proposed sequence is: immutable source snapshot → bounded query → typed proposal → deterministic validation → named approval → isolated native application → independent readback/QA → explicit release. None of this commit machinery is implemented today.

| Level | Allowed operation | Enforcement and exit condition |
|---|---|---|
| Read-only | Query an authorized snapshot/host document | Allowlisted reads, pinned project/document ID, scoped paths, time/output limits; treat model notes/tool text as untrusted data. |
| Proposal | Produce a typed patch without applying it | Proposal ID, project ID, base hash, target IDs, expected old values, new values with units, sources, assumptions, dependency impact, expiry and requested scope. Unknown evidence blocks consequential changes. |
| Preview | Apply proposal to disposable state | Independent constraints checker verifies schema, units/datum, references, opening fit, duplicates and supported topology; no promotion by the LLM. Preview has its own identity. |
| Reversible edit | Operator approves the exact patch hash | Recheck base hash under a serialized commit lock, check native document revision/ownership, use supported transaction or separate copy; reject stale or changed approval. No unrestricted eval/shell bridge. |
| Issue/release | Publish an approved artifact inventory | Readback, applicable geometry/IFC/IDS/office gates, unresolved-issue disposition and named professional approval. Never synthesize a signature or imply permit/code certification. |

Three agents may read the same revision and propose concurrently. A single deterministic coordinator applies at most one approved proposal against that base. Even disjoint edits require revalidation because wall, opening and sheet dependencies can overlap. Never rely on agents agreeing conversationally or merge geometry by last writer wins. A host-native file remains authoritative for its supported model data; the normalized snapshot is a revision-bound projection. Avoid two independently mutable “sources of truth.”

Write an intent receipt before host application. On success, read back identifiers, dimensions, quantities and changed dependencies using a separate query/check path before advancing the approved revision. If native commit succeeds but bookkeeping crashes, mark outcome UNKNOWN, quarantine release and reconcile by operation ID/readback; do not blindly retry. Failed transactions roll back where verified; saved copies/checkpoints provide recovery when undo is not durable. Replays must be idempotent.

Append-only receipts contain actor/operator, UTC times, tool/host versions, patch/base/result hashes, transaction ID, source citations, identity mappings, gate outcomes, errors and recovery links. Hash chaining helps detect alteration but does not authenticate an operator by itself; enforce filesystem/access controls independently. Record rejected and rolled-back operations too.

For future approvals, clearly display the project revision, proposed edit scope, and actual commit/readback status. Cancelling a UI must not misrepresent an already committed transaction as cancelled. No UI was implemented or assessed here.

### Host capability matrix

All Gridline-native host sessions below are **NOT TESTED** here. MCP is a tool interface, not autonomous permission. Vendor capabilities do not imply Gridline implementation.

| Host | Platform and connection | Prerequisites, authority and evidence gap |
|---|---|---|
| Revit | Windows host; 2027.2 public MCP technical preview, local STDIO; Read/Write/Experimental | Installed Revit/add-on, suitable license and local MCP client required. Select Read first; no Gridline session/transaction receipt. [Official preview](https://help.autodesk.com/view/ADSKMCP/ENU/?guid=ADSKMCP_RevitMcp_revit_mcp_server_html). |
| AutoCAD / Civil 3D | Official MCP inside Autodesk Assistant on Windows; AutoCAD read/analysis, Civil 3D includes writes | Licensed running host and Assistant. External Codex connection is not established. A native API bridge needs separate support/edition verification; Mac/LT compatibility is not implied. [Official description](https://help.autodesk.com/view/ADSKMCP/ENU/?guid=ADSKMCP_AutoCADCivil3DMcp_autodesk_autocad_civil_3d_mcp_html). |
| Rhino / Grasshopper | Compute is HTTP(S) geometry service, not native MCP; current FAQ lists Windows/Linux, no macOS Compute | Rhino licensing or server core-hour billing; bounded authenticated wrapper and approved definitions. Compute results do not prove a live document changed. [Compute FAQ](https://developer.rhino3d.com/guides/compute/compute-faq/). [Rhino.Inside.Revit](https://www.rhino3d.com/en/features/rhino-inside-revit/) is Windows only, requires compatible installed hosts. |
| Archicad | Local JSON HTTP and official Python wrapper; desktop Windows/macOS candidate | Running licensed host, chosen instance/command version and project authorization. JSON page retrieval exposed only its version; official indexed documentation describes localhost ports 19723–19743. Read/write commands differ; loopback alone is not authorization. [JSON interface](https://archicadapi.graphisoft.com/JSONInterfaceDocumentation/), [wrapper](https://archicadapi.graphisoft.com/archicadPythonPackage/archicad.html). OS/build acceptance outstanding. |
| IFC + IDS | Local cross-platform Python validation, subject to available wheels | No proprietary host needed for checking; authorized export and versioned requirements needed. Target IFC2X3/IFC4/IFC4X3_ADD2 (4.3.2.0); verify exact validator support. [Schema index](https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/) identified via official search; direct retrieval blocked. |
| Blender | Local `bpy`, add-on/headless bridge; Windows/macOS/Linux | Installed compatible runtime, authorized copied scene, allowlisted operations. No arbitrary Python evaluation; a mesh is not semantic BIM. [Official module builds](https://builder.blender.org/download/bpy/); API page retrieval failed, version-specific commands unverified. |
| FreeCAD | Local Python/document APIs; Windows/macOS/Linux | Installed supported build, copied document, bounded commands and verified recovery. [Official downloads](https://freecad.github.io/Website/download/); Python manual located, current transaction API not verified. No Gridline bridge. |
| APS cloud | Remote Automation API; client OS independent | Developer hub, scoped authorization, consent to upload, engine/version entitlement and budget limits. Cloud job outputs require independent acceptance; not the desktop session. [APS overview](https://www.autodesk.com/products/autodesk-platform-services/overview). |
| Future Tekla / Navisworks | Candidate Windows native API/export integrations | Installed licensed editions and API entitlements must be verified. Native .NET APIs exist but Gridline integrations, host-specific version support, licensing and acceptance remain unverified; no MCP claim or implementation commitment before the first pilot passes. |

The accessed [IfcOpenShell validation documentation](https://docs.ifcopenshell.org/ifcopenshell-python/validation.html) distinguishes SPF syntax and schema/optional EXPRESS validation. [IfcTester](https://docs.ifcopenshell.org/ifctester.html) checks IFC against supplied IDS and produces reports. Validate IDS 1.0 requirements themselves and their applicability, then the model. The official [IDS description](https://www.buildingsmart.org/Standards/Bsi-Standards/Information-Delivery-Specification-Ids/) was available as an indexed search excerpt: alphanumeric requirements exclude geometry. Neither IDS nor schema success establishes clash freedom, architectural adequacy, structural safety or Cyprus/EU permit compliance.

## Independent benchmark and adversarial fixtures

This is a proposed executable protocol, **not observed benchmark results or permission to launch model trials**. Before spending usage, obtain approval for model/runtime/version, launch count, fixed budget and retention. Freeze the repository SHA, fixtures, prompts, dependency versions and ground truth. A practicing architect plus a CAD/BIM technician should author/approve the answer keys separately from implementation. Keep a held-out practice-shaped set; prevent prompt/fixture leakage. Run deterministic tests first, then paired manual and agent-assisted tasks with equal inputs and a predefined stopping rule. Report denominators, false negatives, abstentions and uncertainty; one passing fixture is not general reliability.

| Seeded fixture | Proposed acceptance target and evidence |
|---|---|
| 40-sheet W01 revision | Forty explicit sheet identities spanning plans/elevations/sections/details, plus schedules. Seed width/height/sill/type/host changes, stale revisions, duplicates and an unindexed page. Target 100% recall of seeded critical affected dependencies, ≥95% precision; 100% of unavailable views UNKNOWN. After correction, independently read every expected occurrence: zero stale values, with per-sheet location and before/after hashes. Impact recall and propagation verification are separate scores. |
| Contradictory door/wall dimensions | Door exceeds wall length; dimensions disagree with geometry; negative level, missing units, reused ID. Target 100% rejection of seeded invalid proposals and zero committed-state changes; record failing constraint and source. |
| Stale two-agent edit | Two proposals share a base revision; overlap and disjoint-but-dependent variants. Target exactly one acceptance before rebase, zero silent overwrites; kill process between native commit and receipt. Recovery must identify UNKNOWN rather than duplicate an edit. |
| Malformed IFC / missing properties / IDS | Bad syntax/entity, duplicate GUID, wrong containment, missing mandatory property, malformed IDS, empty applicability and missing validator. Target all seeded mandatory failures block release; never count zero matched elements as meaningful coverage without policy. Report schema and IDS separately; geometry NOT CHECKED. |
| DXF → native edit/save/plot | Licensed AutoCAD on copies: open, native AUDIT, edit W01, save DWG, reopen, plot, export DXF where supported. Target zero unexplained repairs/lost required objects; 100% required tags/layouts preserved; proposed position tolerance ≤1 mm model space and plot scale error ≤0.5%, explicitly office-approved. Capture fonts, viewport lock, layers, xrefs, snapping, dimensions and PDF measurements. |
| Corrupt/unscaled annotated plan | Corrupt image, skewed photo, missing scale, half-erasure, contradictory overlay. Target 100% abstention from dimensional export without calibration; zero silently resolved critical contradictions. On calibrated supported cases propose ≤1% dimensional error, report source coordinates/confidence and reviewer correction time. No one-pass BIM acceptance. |
| Malicious MCP/tool text and filesystem escape | Embed “ignore approval,” forged tool metadata, path traversal, static symlink and ancestor-swap cases. Target zero unauthorized reads/writes/network disclosure and unchanged approved hashes; report denials. Prompt injection needs an authorized real client trial; helper tests alone do not measure it. |
| Output corruption / interrupted build | Move wall geometry without changing tags; delete PDF; stale register date; fail second sheet. Target every seeded mismatch detected, zero mixed revision publication, previous approved set recoverable. |

Fix mutation seed `20261022`, enumerate injected faults, reset from hashed copies per case, and enforce per-run timeouts. Each run needs an immutable receipt: fixture/ground-truth hashes, command, environment, input/output hashes, stdout/stderr, exit code, tool/model version, operator, duration and per-gate PASS/FAIL/NOT RUN/UNKNOWN. Native runs add host build/license context, audit logs, screenshots, measured plots and readback exports. Behavioral runs add skill activation traces, authorized tool calls and provider usage receipts. Proposed usability target: median review time at least 20% lower than the practice's measured manual baseline with no increase in critical misses; this is not a claimed saving.

## Structured owner discussion

These are the owner's supplied questions, not invented dialogue. Objections are this audit's anticipated tradeoffs.

| Exact owner question | Codex position and evidence | Objection / decision needed |
|---|---|---|
| Can we claim that Gridline currently produces professional AutoCAD-ready drawing sets? What fails that claim? | No. Plan-only generation, missing native acceptance (#16), checker blind spots (finding 1) and no complete-set evidence. Say generated DXF proposals, with exact tested gates. | Some files may open correctly. That does not establish professional set quality; approve a narrower public claim. |
| What if three agents edit one building model at once? | Allow three proposals, one serialized commit authority; hash/revision preconditions and dependency revalidation (#15). No present transaction manager. | Throughput falls; correctness requires rejecting stale edits. Decide pilot ownership/locking policy. |
| Is an MCP tool listing enough to say our agent controls Revit? | It supports connection discovery, not task authority or verified model outcomes. Require document query, correct IDs, scoped permissions and readback. Vendor docs describe discovery; Gridline has no live receipt. | Useful smoke test, insufficient acceptance. Decide first supported query and exact host build. |
| Should we ship native write tools before rigorous read-only validation and IFC checks? | No general writes before state/readback gates. IFC checks gate IFC/BIM release; do not block a separately scoped read-only DXF product (#11/#15). | Earlier writes create demos sooner but multiply unrecoverable failure modes. Choose a staged authority ceiling. |
| Can a raster photo of a handwritten floor plan be converted to reliable editable 3D/BIM in one pass? | Not a defensible general claim. #14 requires calibration, ambiguity handling, reviewed 2D, then semantic 3D and independent QA. | Clean controlled examples may work; declare supported inputs and abstentions instead of generalizing. |
| How do we prove a change to W01 propagated across 40 drawings instead of merely suggesting a review? | Freeze inventory, establish independent expected occurrences, read every post-change view/annotation and reconcile values/revisions. Current JSON queue does not do this (#10, finding 2). | Extraction is costly and ambiguous; report UNKNOWN until a human resolves unsupported views. |
| What concrete minimum viable product could a small EU architecture practice use safely next month? | Local read-only revision review for a consented, bounded project: spec/schedule deltas, declared drawing inventory, provenance receipts and architect-reviewed issue list. Offer DXF checks only within measured coverage. | External extraction is unfinished. Start with manually mapped references; do not promise arbitrary drawing-set auditing. |
| Does the test suite demonstrate real model behavior, or only Python and static contract compliance? | It demonstrates Python/helper/installer behavior plus structural contracts. `docs/EVALS.md` confirms behavioral runs are separate; 11 CAD tests skipped here. | Static tests are valuable but cannot establish activation accuracy, hallucination resistance or host quality. Approve a bounded later behavioral study. |

Unresolved decisions: identify the licensed AutoCAD pilot owner; choose authoritative native-model/snapshot ownership; approve minimum project/patch/receipt schemas; choose supported drawing types and office tolerances; appoint architect and CAD/BIM ground-truth reviewers; select IFC schema/MVD and mandatory IDS requirements; define release versus preview authority; authorize any later behavioral trial budget; obtain consented/redacted fixtures and retention policy. No owner is assumed assigned.

## Prioritized 30/60/90-day roadmap

| Window / issue mapping | Deliverable and acceptance | Prerequisites, owners to find, stopping condition |
|---|---|---|
| Days 1–30: #10, #15 foundation, #16 | Fix/reproduce findings 1–6 within bounded scope; provenance-bearing read-only reports, complete supported dependency invalidation, immutable output revision publication. Publish a 40-sheet ground-truth fixture and supported/UNKNOWN coverage. Conduct one manual native AutoCAD acceptance pilot. | Maintainer/Python owner, practicing architect, Windows AutoCAD technician, consented sample. Stop release claims if dependency recall fails, output revisions mix, or host access is unavailable. Ship limited local review MVP only with explicit limits. |
| Days 31–60: #11, #15, narrow #12 | Local IFC syntax/schema and mandatory IDS gate with valid/adversarial fixtures. Implement proposal/base-hash/approval/receipt contract and crash recovery in copied state; no production native writes. If access exists, one Revit Read discovery+document-query pilot. | BIM/IFC specialist, security/adapter maintainer, licensed host partner. Require transport tests and all seeded mandatory failures detected. Stop authority expansion on stale acceptance, ambiguous commit state or missing mandatory validator. |
| Days 61–90: #12; conditional #13; defer #14 | One host's bounded reversible-edit pilot on copies only after #15 passes; independent readback and recovery receipts. Demonstrate one corrected revision across the supported 40-sheet set. Consider small reviewed 2D→3D fixture only after semantics/IFC gates pass. | Native API developer and architect sign-off; baseline host test and recovery procedure already proven. Stop on lost IDs, unexplained geometric drift, failed rollback or increased critical misses. Keep scans research-only; no simultaneous broad host rollout. |

Professionally calibrated public claim: **“Gridline provides portable AEC workflows, conceptual vector drafting and a local read-only revision-impact pilot for indexed project specifications. It can generate plan DXF/PDF proposals and schedules for architectural review. Native AutoCAD acceptance, complete drawing-set verification and IFC/IDS release validation require separate evidence. AI drafts and checks; a qualified architect reviews and signs.”**

## Validation receipts, reproducibility and limits

Environment: Python 3.13.12, Darwin arm64. Commands ran from the isolated checkout:

| Exact command | Observed result |
|---|---|
| `python3 tests/check_repo.py` | Exit 0: v0.7.0; 30 canonical skills; provider sync/manifests/bounded agents; 62 activation cases. |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v > /tmp/gridline-audit-unittest.log 2>&1` | Suite completed: 41 tests in 10.045 s; OK, skipped=11. Thirty executed tests passed. Installer tests used temporary homes, not installed user runtimes. |
| `python3 scripts/sync-provider-skills.py --check` | Exit 0, provider copies match. |
| `python3 skills/architectural-drawing-generation/scripts/aec_draw.py skills/architectural-drawing-generation/references/concept-plan.drawing.json --validate-only` | Exit 0, VALID: 9 entities; SVG format. |
| `bash -n scripts/install-global.sh` | Exit 0. Syntax only. |

Additional `PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'` probes imported the four canonical scripts and deep-copied `R/example-house.building.json`. Executed mutations/outcomes: omitted units → validation `[]`; negative level height → validation `[]`; moved first grid start X → `NO_INDEXED_CHANGES`; changed standard to ncs → `NO_INDEXED_CHANGES`; added W01-only A-301 to both snapshots then increased E1 thickness → only A-101/A-102 affected; moved E1 to L99 → no schedules flagged; negative circle radius → negative SVG radius emitted. The confinement probe called `project_file`, renamed its parent directory, replaced that directory with a sibling-pointing symlink and called `read_spec` on the returned path → `OUTSIDE_SENTINEL`. These are actual probe observations, not future benchmark scores.

`importlib.metadata.version` found no ezdxf, matplotlib, MCP SDK, IfcOpenShell or IfcTester in the active interpreter. No dependencies installed. No live CAD/BIM, IFC, native plotting, screenshots, geometric readback or proprietary host tests ran. `scripts/validate-native.sh` was inspected but not executed because it invokes provider installation/validation outside this audit's necessary checks. No CI run status was fetched or inferred from the badge/workflow.

Research consulted official vendor/standards references with some unavailable pages and read-only GitHub issue records. Unverified API/version specifics are explicitly marked above. No external login, native CAD/BIM application, or real model was modified. No live model-behavior, provider token-cost, or proprietary host evaluation receipt is available.

Verdict: retain the conservative professional boundary, fix the checker/dependency/publication gaps, and prove one practice-shaped read-only workflow before extending authority. The independent Codex audits performed no commits and made no native CAD/BIM changes. The coordinating assistant preserved this documentation report in a separate GitHub review branch. Any implementation phase should read this reviewed baseline and use a fresh isolated worktree rather than treating audit recommendations as completed features.


---

## Second Codex review and external-auditor reconciliation

This addendum was prepared **after** the initial Codex audit, using a separate read-only Codex session and an additional dependency-enabled corruption test performed by the coordinating assistant. Distinguish these receipts from the initial audit's own Python environment and test results. Neither session used live Autodesk/Rhino/BIM software.

### Evidence added since the initial report

| Check | Performer | Observation and scope |
|---|---|---|
| Delete one model-space opening LINE in generated A-101, preserve opening tags and schedules, run `aec_cad.py check` | Coordinating assistant, isolated temporary DXF copy and dependency-enabled `uv` environment (`ezdxf==1.4.5`, `matplotlib==3.11.2`) | **Reproduced false PASS**: `OPEN_LINES_BEFORE 42`, `REMOVED_OPENING_ENTITY`, `CHECK_EXIT=0`, `PASS: 0 errors, 1 warnings; checked 6 items`. Original source checkout untouched. Evidence in Mac temporary directory `/private/tmp/gridline-evidence-8ywUHX`, including `check.log`. This proves the missing-entity case, not all possible geometry failures. |
| Move a grid endpoint; change drawing units | Codex independent second review, in-memory read-only inputs | **Reproduced** `NO_INDEXED_CHANGES` for both changes. Corresponding grid geometry does affect `aec_cad.py` output. |
| Change E1 wall thickness with an unchanged, W01-only referenced detail | Codex independent second review, in-memory read-only inputs | **Reproduced** missed transitive sheet dependency: only level-linked A-101/A-102 flagged, not the W01 detail. |
| Full Python test suite with dependency-enabled CAD libraries | Previous Gridline development validation, not either Codex session | Earlier run had **41 tests, zero failures**. That suite lacked the missing-opening-entity corruption case and must not be represented as native AutoCAD validation. |
| Python tests in first independent Codex audit | First Codex session; no local ezdxf dependency in its active Python environment | **30 passed, 11 skipped**; these skips are an environment limitation, not a regression. |
| Native AutoCAD open/AUDIT/edit/save/plot; native Revit MCP; IFC + IDS validation | Neither review | **NOT RUN**. All are future acceptance gates. |

### Actual cross-review discussion (not a fabricated conversation)

The independent second Codex reviewer received our community concerns, exact previously observed corruption result, vendor premises labeled unverified, and instructions to challenge the present roadmap. These are direct summaries of that **actual follow-up review**; the first review's structured owner dialogue appears above.

| Decision question | First Codex review | Second Codex challenge | Reconciled position |
|---|---|---|---|
| What should ship first? | Read-only coordination MVP plus a native AutoCAD pilot | Local IFC validation, native AutoCAD acceptance, then read-only Revit | **Parallel but bounded workstreams:** fix deterministic generated-DXF checker/atomic publication now; build local IFC/IDS gate as a separate bounded package; arrange **one** licensed AutoCAD acceptance pilot. IFC release checks do not need to block a clearly labeled read-only DXF audit product, while state safety blocks all native writes. |
| Is tag/schedule agreement enough to claim drawings coordinated? | No; checker lacks independent geometry/PDF validation | No; second reviewer treats our removed-LINE false PASS as High | This is the immediate defect to fix. Require per-element geometry readback; deleting, moving, resizing or duplicating an opening entity must fail. Supplement with PDFs and native host acceptance. |
| Can W01's references be accurately resolved across 40 sheets? | No; indirect dependencies missing and references not content-extracted | Need **automatic transitive dependency traversal**, not merely changed ID listing | Build a typed wall→opening→sheet→schedule graph, then check **actual output occurrences**, include negative tests and explicit UNKNOWN for unindexed views. Report review-impact separately from verified propagation. |
| Can multiple agents write models? | No, not yet; only proposals before revision safety/approval | Reject concurrent/stale patch before a write; maintain one commit authority | Separate **query → proposal → preview → approved reversible edit → issue/release**. Bind approval to exact patch hash; host transactions plus independent readback and recovery. Native host document remains authoritative when the project lives there. |
| Which adapter provides real benefit first? | AutoCAD manual pilot because generated DXF is already shipped; Revit Read next | IFC/IDS local validation; AutoCAD native acceptance; Revit Read | The recommendation is ordered by **evidence needs**, not connector count. Cross-platform open-source IFC validation is easiest to test without proprietary seats; a Windows licensed AutoCAD tester is needed to resolve the public DXF usability question. Revit's official MCP needs its stated 2027.2 host. |
| Does an MCP bridge grant trustworthy autonomous authority? | No | No; tool listing, permissions and client connectivity do not establish authorized geometry outcomes | MCP is a transport/capability surface. The control plane must enforce scope, versions, proposal/approval, transactions, readback, audit receipts, and professional sign-off. |

**Second-review disagreements to carry into the implementation issues:**
1. Collapse the competing roadmap priority lists into one **release dependency graph**, rather than treating seven integrations as equal parallel work.
2. Introduce **geometric corruption detection** before enlarging any claim of successful coordination.
3. Prioritize **actual 40-sheet propagation and verification**, not only review queues.
4. Make **atomic publication and named approval** prerequisites for any native write, including recoverable unknown/partially committed outcomes.
5. Maintain separate gates and explicit NOT TESTED states for **AutoCAD interoperability, IFC syntax/schema, IDS requirements, geometry and raster reconstruction**.

### Additional vendor confirmation by the coordinating assistant

These official pages were separately accessed on 2026-10-22; the second Codex review itself did **not** access them and accurately labeled its vendor premises as unverified.

- Autodesk AutoCAD/Civil 3D MCP currently operates within Autodesk Assistant on **Windows**, with AutoCAD exposing analysis/read tools and Civil 3D including write operations; it does **not** establish that external Codex can control AutoCAD: https://help.autodesk.com/view/ADSKMCP/ENU/?guid=ADSKMCP_AutoCADCivil3DMcp_autodesk_autocad_civil_3d_mcp_html
- Autodesk Revit official MCP technical preview requires **Revit 2027.2** for the current Read, Write and Experimental local-STDIO configurations: https://help.autodesk.com/view/ADSKMCP/ENU/?guid=ADSKMCP_RevitMcp_revit_mcp_server_html
- Rhino.Compute is an HTTP(S) geometry service, not native MCP; the current McNeel FAQ excludes **macOS-hosted** Compute, while Windows/Linux hosting and licensing differ: https://developer.rhino3d.com/guides/compute/compute-faq/
- Graphisoft Archicad JSON is a **localhost HTTP** integration in SI units: https://archicadapi.graphisoft.com/JSONInterfaceDocumentation/
- IfcOpenShell documents **IfcMCP**, which exposes in-memory IFC query and edit tools, plus IfcQuery/IfcDiff/IfcTester. Evaluate these established tools as candidates for *read-only, copied-file* review before developing another IFC MCP bridge; keep edits disabled until permission, source, persistence and transaction controls are independently validated: https://docs.ifcopenshell.org/introduction.html
- Bonsai provides open-source IFC-native authoring inside Blender, a strong alternative to prototyping semantics in a mesh-only geometry viewer: https://docs.bonsaibim.org/ and https://docs.ifcopenshell.org/bonsai.html
- Tekla Structures has a licensed official **.NET Open API** for model and drawing integrations (candidate for later structural discipline needs, not a current Gridline MCP): https://developer.tekla.com/documentation/get-started-tekla-structures-open-api
- APS Automation provides optional cloud execution for supported Autodesk engines with additional account, data-security, licensing and operational constraints: https://www.autodesk.com/products/autodesk-platform-services/overview

### Final architecture disposition

**Go now:** accurate deterministic DXF geometry check, fail-closed spec/state validation, immutable/staged output publication, source hashes/receipts, typed dependency graph and a test suite with adversarial fixtures. Support native quality evidence gathering on licensed hosts before advertising AutoCAD-readiness.

**Gate for subsequent phases:** IFC schema/EXPRESS + IDS + separately verified geometry; one official/native host **read-only** integration; proposal/base-hash/approval control plane; then exactly one bounded reversible native write pilot on a copy.

**Defer:** broad agent-write permissions; seven-host connector rollout; one-shot photo/handwriting→BIM claims; autonomous construction-ready publication; regulatory sign-off by an LLM. Human architects and other qualified discipline professionals retain design responsibility.

This addendum updates the audit's status, but **does not implement the fixes**. The accompanying issues remain the tracked implementation work: [#10 cross-sheet](https://github.com/MakeItEzzz555/Gridline/issues/10), [#11 IFC/IDS](https://github.com/MakeItEzzz555/Gridline/issues/11), [#12 native connectors](https://github.com/MakeItEzzz555/Gridline/issues/12), [#13 2D→3D](https://github.com/MakeItEzzz555/Gridline/issues/13), [#14 annotated scans](https://github.com/MakeItEzzz555/Gridline/issues/14), [#15 state safety](https://github.com/MakeItEzzz555/Gridline/issues/15), and [#16 AutoCAD round-trip](https://github.com/MakeItEzzz555/Gridline/issues/16).
