# Overview

## Purpose
Collect and normalize NSE corporate data for downstream agent and automation workflows.

## Description
A CLI designed to fetch and normalize selected corporate-data disclosures from the National Stock Exchange (NSE) of India.

The implemented CLI currently supports two workflows:

- `further-issues`: preferential allotments (`PREF`), QIPs (`QIP`), or both
- `insider-trading`: insider trading disclosures

Each workflow fetches filing metadata from NSE, downloads linked XBRL documents, enriches rows with four-level industry mapping from `eggmasonvalue/stock-industry-map-in`, fetches Current Market Price (CMP) for stock symbols when that data is relevant, and writes normalized JSON output. For insider trading, CMP fetches are limited to `Market Purchase` and `Market Sale` rows. Robust retry mechanisms (via `tenacity`) ensure consistency during API flakes.

For insider trading, XBRL processing is optional and controlled by configuration; it is disabled by default because the API payload is currently sufficient.

The project depends on `nse-xbrl-parser`, resolved by `uv` from the GitHub HTTPS repository at `https://github.com/eggmasonvalue/nse-xbrl-parser.git`.

## CLI Usage
The application provides a CLI (`uv run nse-corporate-data`) with dedicated subcommands for each workflow. The `further-issues` command accepts `--from-date`, optional `--to-date`, and repeatable canonical `--category` values (`pref`, `qip`); omitting `--category` means both. The `insider-trading` command accepts `--from-date`, optional `--to-date`, and repeatable canonical `--mode` tokens; it defaults to `market`, which expands to `Market Purchase` and `Market Sale`. Execution runs silently, diverting all logging to `cli.log`, making it LLM-agent friendly. Outputs are saved as normalized JSON files.
