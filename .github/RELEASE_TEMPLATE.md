# nse-corporate-data CLI Release

This release contains the compiled, standalone executable for `nse-corporate-data`.

## AI Agent Instructions

You are equipped to use this standalone CLI to fetch and parse corporate data from the NSE. This binary requires no Python environment or dependencies to run.

### Setup
1. Download the correct executable attached to this release for your operating system and architecture.
2. For Linux and macOS, make it executable: `chmod +x <filename>`

### Usage Strategy
The CLI is self-documenting. **Aggressively use the `--help` flag** to explore available commands, subcommands, and options before running commands.

Start by exploring the top-level commands:
```bash
./<filename> --help
```

Then explore subcommands, for example:
```bash
./<filename> further-issues --help
./<filename> further-issues fetch --help
```

### Outputs
The tool generally operates silently but will write data to standard JSON output files (e.g., `pref_data.json`, `insider_trading_short.json`). Rely on the CLI help and output files to determine what operations were successful.