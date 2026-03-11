# Overview

## Purpose
Track preferential allotments, rights issues, and QIPs (Qualified Institutional Placements) of NSE-listed companies.

## Description
A tool designed to monitor and track further issues (preferential allotments, rights issues, QIPs) of companies listed on the National Stock Exchange (NSE) of India.

## CLI Usage (v0.1)
The application provides a CLI (`uv run further-issue-tracker fetch`) to fetch and parse XBRL information. The CLI supports querying data by date range (`--from-date`, `--to-date`) and by listing category (`--category PREF`, `QIP` or `BOTH`). Execution runs silently, diverting all logging to `cli.log`, making it LLM-agent friendly. Outputs are saved in JSON formulation.
