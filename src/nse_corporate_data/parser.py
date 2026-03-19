import json
import logging
from typing import Any, Dict, Iterable, List, Optional
from nse_xbrl_parser import parse_xbrl_file

logger = logging.getLogger(__name__)
_CMP_RELEVANT_ACQ_MODES = {"Market Purchase", "Market Sale"}


def _empty_results() -> Dict[str, Any]:
    return {
        "metadata": {
            "api": [],
            "xbrl": [],
            "industry": [],
            "CMP": ["CMP"],
        },
        "data": [],
    }


def _resolve_first(item: Dict[str, Any], keys: Iterable[str]) -> Optional[Any]:
    for key in keys:
        value = item.get(key)
        if value:
            return value
    return None


def _extract_cmp(quote_data: Dict[str, Any]) -> Optional[Any]:
    price_info = quote_data.get("priceInfo", {})
    for key in ("close", "lastPrice", "previousClose"):
        value = price_info.get(key)
        if value not in (None, 0, 0.0, "0", "0.0"):
            return value
    return None


def parse_filings_data(
    filings: List[Dict[str, Any]],
    fetcher: Any,
    symbol_keys: Iterable[str],
    xbrl_keys: Iterable[str],
    enable_xbrl_processing: bool = True,
) -> Dict[str, Any]:
    """
    Given a list of JSON payload items from NSE, extract metadata into a dict
    with "metadata" headers and normalized row data.
    """
    if not filings:
        return _empty_results()

    # Dynamically extract all unique API keys from NSE JSON payloads
    unique_api_keys = set()
    for item in filings:
        unique_api_keys.update(item.keys())

    sorted_api_keys = sorted(list(unique_api_keys))

    # PASS 1: Fetch and parse all XBRL dicts, collect all unique XBRL keys
    records = []
    unique_xbrl_keys = set()

    for item in filings:
        base_row = [item.get(key) for key in sorted_api_keys]

        symbol = _resolve_first(item, symbol_keys)
        if not symbol:
            symbol = "UNKNOWN"

        xbrl_url = _resolve_first(item, xbrl_keys)
        parsed_xbrl = {}

        if enable_xbrl_processing and xbrl_url:
            xml_path = fetcher.download_xbrl_file(xbrl_url)
            if xml_path and xml_path.exists():
                try:
                    logger.debug(f"Parsing XBRL file: {xml_path}")
                    xbrl_data = parse_xbrl_file(str(xml_path))
                    if xbrl_data and isinstance(xbrl_data, dict):
                        parsed_xbrl = xbrl_data
                        unique_xbrl_keys.update(parsed_xbrl.keys())
                except Exception as e:
                    logger.error(f"Failed to parse XBRL file {xml_path}: {e}")

        records.append(
            {
                "symbol": symbol,
                "base_row": base_row,
                "xbrl_dict": parsed_xbrl,
                "source_item": item,
            }
        )

    # PASS 2: Construct metadata and flattened data arrays
    sorted_xbrl_keys = sorted(list(unique_xbrl_keys))
    industry_data = fetcher.get_industry_data()
    industry_metadata = industry_data.get("metadata", [])
    industry_map = industry_data.get("data", {})

    results = {
        "metadata": {
            "api": sorted_api_keys,
            "xbrl": sorted_xbrl_keys,
            "industry": industry_metadata,
            "CMP": ["CMP"],
        },
        "data": [],
    }

    for rec in records:
        symbol = rec["symbol"]
        source_item = rec["source_item"]
        xbrl_values = [rec["xbrl_dict"].get(k) for k in sorted_xbrl_keys]

        # Fetch CMP
        cmp = None
        acq_mode = source_item.get("acqMode")
        if symbol != "UNKNOWN" and acq_mode in _CMP_RELEVANT_ACQ_MODES:
            quote_data = fetcher.get_quote(symbol)
            if quote_data:
                cmp = _extract_cmp(quote_data)

        # Get industry data for this symbol
        industry_values = industry_map.get(symbol, [])

        results["data"].append(
            {
                "symbol": symbol,
                "api": rec["base_row"],
                "xbrl": xbrl_values,
                "industry": industry_values,
                "CMP": cmp,
            }
        )

    return results


def save_to_json(data: Dict[str, Any], output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

    count = len(data.get("data", []))
    logger.info(f"Saved {count} records to {output_path}")
