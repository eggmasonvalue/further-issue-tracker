import subprocess
from pathlib import Path
import sys


def run_command(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error executing command:\n{result.stderr}")
        sys.exit(result.returncode)
    print(result.stdout)


def main():
    root_dir = Path(__file__).parent.parent
    samples_dir = root_dir / "samples"
    samples_dir.mkdir(exist_ok=True)

    # ---------------------------------------------------------
    # PART 1: FULLY ENRICHED
    # ---------------------------------------------------------
    print("\n--- ENRICHED SAMPLES ---")
    print("Fetching Further Issues (10-Mar to 21-Mar) [ENRICHED]...")
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "further-issues",
            "fetch",
            "--from-date",
            "10-03-2026",
            "--to-date",
            "21-03-2026",
            "--enrich",
            "market-data",
            "--enrich",
            "industry",
            "--enrich",
            "xbrl",
        ],
        cwd=samples_dir,
    )

    print("Refining Further Issues [ENRICHED]...")
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "further-issues",
            "refine",
            "--category",
            "pref",
        ],
        cwd=samples_dir,
    )
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "further-issues",
            "refine",
            "--category",
            "qip",
        ],
        cwd=samples_dir,
    )

    print("Fetching Insider Trading (21-Mar) [ENRICHED]...")
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "insider-trading",
            "fetch",
            "--from-date",
            "21-03-2026",
            "--to-date",
            "21-03-2026",
            "--enrich",
            "market-data",
            "--enrich",
            "industry",
            "--enrich",
            "xbrl",
        ],
        cwd=samples_dir,
    )

    print("Refining Insider Trading [ENRICHED]...")
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "insider-trading",
            "refine",
            "--preset",
            "market",
        ],
        cwd=samples_dir,
    )

    # ---------------------------------------------------------
    # PART 2: UNENRICHED
    # ---------------------------------------------------------
    print("\n--- UNENRICHED SAMPLES ---")
    print("Fetching Further Issues (10-Mar to 21-Mar) [UNENRICHED]...")
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "further-issues",
            "fetch",
            "--from-date",
            "10-03-2026",
            "--to-date",
            "21-03-2026",
        ],
        cwd=samples_dir,
    )

    # Rename the un-enriched raw files
    (samples_dir / "pref_raw.json").rename(samples_dir / "pref_unenriched_raw.json")
    (samples_dir / "qip_raw.json").rename(samples_dir / "qip_unenriched_raw.json")

    print("Refining Further Issues [UNENRICHED]...")
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "further-issues",
            "refine",
            "--category",
            "pref",
            "--input",
            "pref_unenriched_raw.json",
            "--output",
            "pref_unenriched.json",
        ],
        cwd=samples_dir,
    )
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "further-issues",
            "refine",
            "--category",
            "qip",
            "--input",
            "qip_unenriched_raw.json",
            "--output",
            "qip_unenriched.json",
        ],
        cwd=samples_dir,
    )

    print("Fetching Insider Trading (21-Mar) [UNENRICHED]...")
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "insider-trading",
            "fetch",
            "--from-date",
            "21-03-2026",
            "--to-date",
            "21-03-2026",
        ],
        cwd=samples_dir,
    )

    # Rename the un-enriched raw file
    (samples_dir / "insider_raw.json").rename(samples_dir / "insider_unenriched_raw.json")

    print("Refining Insider Trading [UNENRICHED]...")
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "insider-trading",
            "refine",
            "--preset",
            "market",
            "--input",
            "insider_unenriched_raw.json",
            "--output",
            "insider_unenriched.json",
        ],
        cwd=samples_dir,
    )

    # Re-run ENRICHED fetch to restore the default output files
    # (Since the unenriched step overwrites them before we rename them)
    print("\n--- RESTORING DEFAULT ENRICHED RAW FILES ---")
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "further-issues",
            "fetch",
            "--from-date",
            "10-03-2026",
            "--to-date",
            "21-03-2026",
            "--enrich",
            "market-data",
            "--enrich",
            "industry",
            "--enrich",
            "xbrl",
        ],
        cwd=samples_dir,
    )
    run_command(
        [
            "uv",
            "run",
            "nse-corporate-data",
            "insider-trading",
            "fetch",
            "--from-date",
            "21-03-2026",
            "--to-date",
            "21-03-2026",
            "--enrich",
            "market-data",
            "--enrich",
            "industry",
            "--enrich",
            "xbrl",
        ],
        cwd=samples_dir,
    )


    print("Sample generation complete.")


if __name__ == "__main__":
    main()
