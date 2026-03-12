# further-issue-tracker

CLI tool for collecting NSE further-issue filing data, downloading linked XBRL documents, flattening the result into JSON, and rendering presentable static HTML views.

## What it does

The project currently fetches and parses:

- Preferential allotment filings (`PREF`)
- Qualified Institutional Placement filings (`QIP`)

For each filing, the CLI:

1. Calls the relevant NSE corporate filings API for a date range.
2. Downloads the linked XBRL document when one is present.
3. Parses the XBRL into a flat dictionary using `nse-xbrl-parser`.
4. Writes normalized JSON output files for downstream processing.
5. Renders self-contained HTML views beside each JSON artifact.

## Requirements

- Python 3.12+
- `uv`

## Installation

Install dependencies with:

```bash
uv sync
```

`uv` resolves `nse-xbrl-parser` directly from `https://github.com/eggmasonvalue/nse-xbrl-parser.git`.

## Usage

Run the CLI with:

```bash
uv run further-issue-tracker fetch --from-date DD-MM-YYYY --to-date DD-MM-YYYY --category PREF|QIP|BOTH
```

Example:

```bash
uv run further-issue-tracker fetch --from-date 01-03-2026 --to-date 12-03-2026 --category BOTH
```

Render existing root JSON files into HTML without refetching:

```bash
uv run further-issue-tracker render
```

### Arguments

- `--from-date`: start date in `DD-MM-YYYY`
- `--to-date`: end date in `DD-MM-YYYY`
- `--category`: `PREF`, `QIP`, or `BOTH`

## Outputs

The command is intentionally silent on stdout/stderr. Inspect these files after a run:

- `cli.log`: execution log, overwritten on each run
- `pref_data.json`: output for `PREF`
- `qip_data.json`: output for `QIP`
- `pref_data.html`: presentable HTML view for `pref_data.json`
- `qip_data.html`: presentable HTML view for `qip_data.json`

When `--category BOTH` is used, both JSON and HTML files are produced.

Output shape:

```json
{
  "metadata": {
    "api": ["..."],
    "xbrl": ["..."]
  },
  "data": {
    "SYMBOL": {
      "api": ["..."],
      "xbrl": ["..."]
    }
  }
}
```

- `metadata.api`: sorted keys observed in the NSE API payload
- `metadata.xbrl`: sorted keys observed across parsed XBRL documents
- `data[SYMBOL].api`: row values aligned to `metadata.api`
- `data[SYMBOL].xbrl`: row values aligned to `metadata.xbrl`

The HTML renderer uses those metadata arrays to label each section, adds dataset summary cards, highlights top entities by the most informative numeric metric, and renders filterable tables for both `api` and `xbrl`.

## Project Structure

- `src/further_issue_tracker/cli.py`: Click CLI entrypoint and input validation
- `src/further_issue_tracker/fetcher.py`: NSE session management, filing fetches, XBRL downloads
- `src/further_issue_tracker/parser.py`: XBRL parsing and JSON serialization
- `src/further_issue_tracker/renderer.py`: static HTML rendering for root JSON artifacts

## Agent Skill

The JSON outputs are suitable for agent-side presentation with the standalone `render-json-ui` skill:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo eggmasonvalue/render-json-ui-skill \
  --path render-json-ui
```

Restart Codex after installation so it can load the skill.

## Testing

Run:

```bash
uv run pytest
```

Current automated coverage is still light, but renderer coverage now checks HTML generation, root JSON discovery, and default CLI render behavior.
