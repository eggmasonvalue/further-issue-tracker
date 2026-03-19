# Architecture

```mermaid
graph TD
    subgraph nse-corporate-data
        cli[cli.py]
        fetcher[fetcher.py]
        parser[parser.py]
        
        cli --> fetcher
        cli --> parser
        fetcher --> nse[NSE APIs]
        fetcher --> industry[stock-industry-map-in GitHub]
        parser --> nsexbrl[nse_xbrl_parser]
        parser --> json[JSON artifacts]
    end
```

`cli.py` exposes separate `further-issues` and `insider-trading` commands. Both commands use canonical machine-facing repeatable options rather than upstream NSE labels: `--category pref|qip` for further issues and `--mode ...` tokens for insider trading, with internal expansion back to the raw NSE values. `fetcher.py` owns NSE session setup, JSON endpoint fetches, XBRL downloads, quote lookups, and cached industry-map retrieval; quote responses are cached per symbol to avoid repeated NSE hits within a run. `parser.py` normalizes heterogeneous NSE payloads through configurable symbol/XBRL field mapping, enriches each row with industry and CMP data, and can skip insider-trading XBRL parsing entirely when configuration disables it.
