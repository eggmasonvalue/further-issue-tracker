# Changelog
## [Unreleased]
- Changed CMP extraction to use NSE quote priority `close`, then `lastPrice`, then `previousClose`, while treating zero-valued quote fields as missing so fallbacks can apply.
- Limited insider-trading CMP lookups to `Market Purchase` and `Market Sale` rows to avoid unnecessary quote calls.
- Added `Settings`-based configuration for insider trading, including `NSE_CORPORATE_DATA_ENABLE_INSIDER_TRADING_XBRL`.
- Disabled insider-trading XBRL processing by default while keeping it configurable.
- Added a fetcher-level per-symbol quote cache to avoid repeated NSE quote requests within a run.
- Replaced raw CLI values with canonical machine-facing tokens: repeatable `--category pref|qip` for further issues and repeatable `--mode` tokens for insider trading.
- Renamed insider mode tokens `buy` and `sell` to `market-buy` and `market-sell` to avoid ambiguity with broader NSE buy/sell semantics.
- Renamed the project/package surface to `nse-corporate-data` / `nse_corporate_data`.
- Replaced the old single `fetch` command with `further-issues` and `insider-trading`.
- Changed the further-issues CLI option from `--category` to `--categories`.
- Added a default `--to-date` of the local run date for both CLI workflows.
- Added a default `--categories` value of `BOTH` for further-issues.
- Added insider trading ingestion using the NSE `corporates-pit` endpoint, XBRL download, industry enrichment, and CMP enrichment.
- Added tests covering CLI defaults, date-range validation, and generic parser behavior.
- Documented the temporary insider-trading XBRL parsing limitation caused by upstream NSE taxonomy issues.

## [0.3.0] - 2026-03-18
- Added `tenacity` dependency and implemented a retry mechanism for NSE API failures (`TimeoutError`, `ConnectionError`, and status codes 408, 429, 502, 503, 504).
- Added `CMP` to the metadata dictionary so that the Current Market Price entry is commensurate with best practices.
- Added four-level industry mapping (Macro, Sector, Industry, Basic Industry) for all stocks in the output, fetched from `eggmasonvalue/stock-industry-map-in`.
- Added Current Market Price (CMP) fetching for stock symbols in corporate filings using the `nse` dependency's `quote` method.
...
- Improved CLI `fetch` command to return a minimal JSON object with essential results (`files` or `error`).
- Implemented stdout/stderr redirection to the log file during CLI execution to ensure clean JSON output while capturing external messages.
- Switched the `nse-xbrl-parser` dependency source from a local path checkout to the GitHub HTTPS repository URL.
- Replaced the placeholder README with usage, output, and structure documentation aligned to the current CLI behavior.

## [0.2.0] - 2026-03-12
- Modified CLI to overwrite `cli.log` on each run instead of appending.
- Integrated `nse` server dependency for bot-protected API requests.
- Added `nse-xbrl-parser` for processing corporate filing XBRL documents.
- Implemented Click CLI with `fetch` command to query PREF, QIP, or BOTH listing metadata between given dates.
- Output formats standardized as JSON logs with robust parameter validation to prevent hallucinated inputs.
- Initial project scaffold
