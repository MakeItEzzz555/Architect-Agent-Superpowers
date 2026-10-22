# Coordinated CAD pipeline: design record (0.6.0)

## Why
Architects spend most of their hours producing and coordinating construction documents. A drawing an agent produces is only useful if it uses the office's CAD standard, sits on a correctly scaled sheet, and agrees with every schedule. The pack previously produced six-primitive diagrams.

## Decisions
- **Audience:** small practices and independent architects, Cyprus/EU first; standards configurable for anywhere.
- **One source of truth:** a JSON building spec (mm). DXF sheets, PDFs, schedules and the sheet register are all derived from it; nothing is hand-edited.
- **Real CAD output:** ezdxf (optional dependency) writes R2018 DXF with model-space geometry at 1:1 and paper-space sheets with locked viewports, so files open in AutoCAD and other CAD tools as a drafter would set them up.
- **Configurable standards:** ISO 13567 (default) and US NCS profiles; offices `extend` them.
- **Independent checker:** `check` reads files back from disk, so it verifies what was delivered rather than what the builder intended.
- **Professional boundary:** status stamp by default; issued statuses require a named checker.

## Not in this release
Sections, elevations, details, stairs, furniture, imperial units, IFC export, live AutoCAD control. See ROADMAP.md for the order.
