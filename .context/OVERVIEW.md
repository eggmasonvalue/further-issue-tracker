# Overview

## Purpose
Track preferential allotments, rights issues, and QIPs (Qualified Institutional Placements) of NSE-listed companies, with root-level JSON artifacts rendered into readable static HTML.

## Description
A tool designed to monitor and track further issues of companies listed on the National Stock Exchange (NSE) of India.

The implemented CLI currently supports preferential allotments (`PREF`) and QIPs (`QIP`) by fetching filing metadata from NSE, downloading linked XBRL documents, writing normalized JSON output, and rendering companion HTML views (`pref_data.html`, `qip_data.html`).

The project depends on `nse-xbrl-parser`, resolved by `uv` from the GitHub HTTPS repository at `https://github.com/eggmasonvalue/nse-xbrl-parser.git`.

The generated JSON artifacts are designed to be consumable by external agent workflows, including the standalone `render-json-ui` skill distributed from `eggmasonvalue/render-json-ui-skill`.

## CLI Usage
The application provides a CLI with two commands:

- `uv run further-issue-tracker fetch` fetches and parses XBRL information by date range (`--from-date`, `--to-date`) and listing category (`--category PREF`, `QIP` or `BOTH`). Execution runs silently, diverting all logging to `cli.log`, and emits JSON plus HTML artifacts.
- `uv run further-issue-tracker render` re-renders any root `*_data.json` artifacts into self-contained HTML without refetching.
