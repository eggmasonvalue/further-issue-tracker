# Changelog

## [Unreleased]
- Added `src/further_issue_tracker/renderer.py` to turn root `*_data.json` artifacts into self-contained HTML views with summary cards, highlights, filterable tables, and section navigation.
- Added a `render` CLI command and updated `fetch` to emit HTML companions automatically after writing JSON.
- Added renderer-focused tests covering HTML generation, artifact discovery, and default render behavior.
- Switched the `nse-xbrl-parser` dependency source from a local path checkout to the GitHub HTTPS repository URL.
- Replaced the placeholder README with usage, output, and structure documentation aligned to the current CLI behavior.
- Added installation guidance for the standalone `render-json-ui` agent skill that can present the generated JSON artifacts.

## [0.2.0] - 2026-03-12
- Modified CLI to overwrite `cli.log` on each run instead of appending.
- Integrated `nse` server dependency for bot-protected API requests.
- Added `nse-xbrl-parser` for processing corporate filing XBRL documents.
- Implemented Click CLI with `fetch` command to query PREF, QIP, or BOTH listing metadata between given dates.
- Output formats standardized as JSON logs with robust parameter validation to prevent hallucinated inputs.
- Initial project scaffold
