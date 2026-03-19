from typing import Any, Dict, List

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
