# Design

## Features
- Implemented: Track Preferential Allotments
- Implemented: Track QIPs
- Implemented: Track insider trading disclosures
- Implemented: NSE Data Integration with XBRL download and parsing
- Implemented: Four-level industry mapping (Macro, Sector, Industry, Basic Industry) integration
- Implemented: Current Market Price (CMP) fetching for stock symbols
- Implemented: Per-symbol quote caching to avoid repeated quote calls inside a run
- Implemented: Insider-trading CMP fetch limited to `Market Purchase` and `Market Sale` rows
- Implemented: CMP field priority of `close`, then `lastPrice`, then `previousClose`
- Implemented: Tenacity-based retry mechanism for resilient API requests
- Implemented: CLI execution with structured JSON output; internal stdout/stderr redirected to log file
- Implemented: Coherent top-level CLI workflows (`further-issues`, `insider-trading`)
- Implemented: Canonical machine-facing `--category` and `--mode` CLI tokens with internal mapping to NSE values
- Not implemented: Rights Issues workflow
- Known limitation: Insider trading XBRL parsing can fail until NSE fixes the published taxonomy/schema resolution; the workflow now defaults to skipping insider XBRL unless explicitly enabled

## Note:
use "revisedFlag" to deduplicate filings while developing on top of this
