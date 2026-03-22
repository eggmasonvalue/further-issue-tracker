from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional, Sequence


@dataclass(frozen=True)
class RefinedField:
    name: str
    extractor: Callable[[Mapping[str, Any]], Any]
    requires: Optional[str] = None


def build_refined_output(
    full_output: Mapping[str, Any],
    fields: Sequence[RefinedField],
) -> Dict[str, Any]:
    metadata = full_output.get("metadata", {})
    api_fields = metadata.get("api", [])

    active_fields = [
        f for f in fields
        if f.requires is None or f.requires in metadata
    ]

    results: Dict[str, Any] = {
        "metadata": {
            "record": [field.name for field in active_fields],
        },
        "data": [],
    }

    if "industry" in metadata:
        results["metadata"]["industry"] = metadata["industry"]
    if "marketData" in metadata:
        results["metadata"]["marketData"] = metadata["marketData"]

    for row in full_output.get("data", []):
        context = dict(zip(api_fields, row.get("api", [])))
        if "symbol" not in context and row.get("symbol") is not None:
            # Backward compatibility for previously generated full artifacts.
            context["symbol"] = row.get("symbol")

        if "xbrl" in row and "xbrl" in metadata:
            context.update(dict(zip(metadata["xbrl"], row["xbrl"])))
        if "industry" in row and "industry" in metadata:
            context.update(dict(zip(metadata["industry"], row["industry"])))
        if "marketData" in row and "marketData" in metadata:
            context.update(dict(zip(metadata["marketData"], row["marketData"])))

        row_out = {
            "record": [field.extractor(context) for field in active_fields],
        }
        if "industry" in row:
            row_out["industry"] = row["industry"]
        if "marketData" in row:
            row_out["marketData"] = row["marketData"]

        results["data"].append(row_out)

    return results
