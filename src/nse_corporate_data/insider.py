from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Callable, Dict, List, Mapping, Sequence

INSIDER_MODE_TO_ACQ_MODE = {
    "unknown": ("-",),
    "bonus": ("Bonus",),
    "conversion": ("Conversion of security",),
    "esop": ("ESOP",),
    "gift": ("Gift",),
    "inter-se-transfer": ("Inter-se-Transfer",),
    "pledge-invoke": ("Invocation of pledge",),
    "market": ("Market Purchase", "Market Sale"),
    "market-buy": ("Market Purchase",),
    "market-sell": ("Market Sale",),
    "off-market": ("Off Market",),
    "others": ("Others",),
    "pledge-create": ("Pledge Creation",),
    "preferential-offer": ("Preferential Offer",),
    "public-right": ("Public Right",),
    "pledge-revoke": ("Revokation of Pledge",),
    "scheme": ("Scheme of Amalgamation/Merger/Demerger/Arrangement",),
}

INSIDER_MODES = tuple(INSIDER_MODE_TO_ACQ_MODE.keys())
DEFAULT_INSIDER_MODES = ("market",)
DEFAULT_INSIDER_FULL_OUTPUT = "insider_trading_data.json"
DEFAULT_INSIDER_SHORT_OUTPUT = "insider_trading_short.json"


@dataclass(frozen=True)
class InsiderShortField:
    name: str
    extractor: Callable[[Mapping[str, Any]], Any]


def _to_decimal(value: Any) -> Decimal | None:
    if value in (None, "", "-", "None"):
        return None
    try:
        return Decimal(str(value).replace(",", ""))
    except (InvalidOperation, ValueError):
        return None


def _coerce_number(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if value == value.to_integral():
        return int(value)
    return float(value)


def _trade_date(context: Mapping[str, Any]) -> str | None:
    from_date = context.get("acqfromDt")
    to_date = context.get("acqtoDt")
    if from_date and to_date and from_date != to_date:
        return f"{from_date} to {to_date}"
    return to_date or from_date


def _price_per_share(context: Mapping[str, Any]) -> int | float | None:
    transaction_value = _to_decimal(context.get("secVal"))
    quantity = _to_decimal(context.get("secAcq"))
    if transaction_value is None or quantity in (None, Decimal("0")):
        return None
    return _coerce_number(transaction_value / quantity)


def _holding_delta_pct(context: Mapping[str, Any]) -> int | float | None:
    before = _to_decimal(context.get("befAcqSharesPer"))
    after = _to_decimal(context.get("afterAcqSharesPer"))
    if before is None or after is None:
        return None
    return _coerce_number(after - before)


INSIDER_SHORT_FIELDS: Sequence[InsiderShortField] = (
    InsiderShortField("symbol", lambda context: context.get("symbol")),
    InsiderShortField("company", lambda context: context.get("company")),
    InsiderShortField("acqMode", lambda context: context.get("acqMode")),
    InsiderShortField("tradeDate", _trade_date),
    InsiderShortField(
        "transactionValue",
        lambda context: _coerce_number(_to_decimal(context.get("secVal"))),
    ),
    InsiderShortField("pricePerShare", _price_per_share),
    InsiderShortField("CMP", lambda context: context.get("CMP")),
    InsiderShortField("holdingDeltaPct", _holding_delta_pct),
    InsiderShortField("Macro", lambda context: context.get("Macro")),
    InsiderShortField("Sector", lambda context: context.get("Sector")),
    InsiderShortField("Industry", lambda context: context.get("Industry")),
    InsiderShortField("Basic Industry", lambda context: context.get("Basic Industry")),
)


def filter_insider_filings_by_mode(
    filings: List[Dict[str, Any]], modes: tuple[str, ...]
) -> List[Dict[str, Any]]:
    if not modes:
        return filings

    allowed_modes = {
        acq_mode
        for mode in modes
        for acq_mode in INSIDER_MODE_TO_ACQ_MODE[mode]
    }
    return [item for item in filings if item.get("acqMode") in allowed_modes]


def build_insider_short_output(
    full_output: Mapping[str, Any],
    fields: Sequence[InsiderShortField] = INSIDER_SHORT_FIELDS,
) -> Dict[str, Any]:
    metadata = full_output.get("metadata", {})
    api_fields = metadata.get("api", [])
    industry_fields = metadata.get("industry", [])

    results: Dict[str, Any] = {
        "metadata": [field.name for field in fields],
        "data": [],
    }

    for row in full_output.get("data", []):
        context = {
            "symbol": row.get("symbol"),
            "CMP": row.get("CMP"),
        }
        context.update(dict(zip(api_fields, row.get("api", []))))
        context.update(dict(zip(industry_fields, row.get("industry", []))))
        results["data"].append([field.extractor(context) for field in fields])

    return results
