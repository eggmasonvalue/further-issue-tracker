import html
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


NUMERIC_HINTS = (
    "amount",
    "size",
    "price",
    "shares",
    "allottee",
    "discount",
    "raised",
    "issue",
)
DATE_HINTS = ("date", "dt", "listing", "submission", "approval")


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None

    compact = value.replace(",", "").strip()
    if not compact or compact.endswith("KB"):
        return None

    try:
        return float(compact)
    except ValueError:
        return None


def _coerce_date(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None

    for fmt in ("%d-%b-%Y", "%d-%B-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _format_number(value: float) -> str:
    if value.is_integer():
        return f"{int(value):,}"
    return f"{value:,.2f}"


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        if not value:
            return "[]"
        head = ", ".join(str(item) for item in value[:3])
        suffix = "" if len(value) <= 3 else f", +{len(value) - 3} more"
        return f"[{head}{suffix}]"
    if isinstance(value, dict):
        return f"{{{len(value)} fields}}"

    text = str(value)
    if len(text) > 140:
        return f"{text[:137]}..."
    return text


def _html_cell(value: Any) -> str:
    return html.escape(_format_value(value))


def _humanize(name: str) -> str:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name.replace("_", " "))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:1].upper() + text[1:] if text else name


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "section"


def _normalize_rows(payload: dict[str, Any], section: str) -> list[dict[str, Any]]:
    metadata = payload.get("metadata", {})
    columns = metadata.get(section, []) if isinstance(metadata, dict) else []
    entities = payload.get("data", {})
    rows: list[dict[str, Any]] = []

    if not isinstance(columns, list) or not isinstance(entities, dict):
        return rows

    for entity_key, record in entities.items():
        if not isinstance(record, dict):
            continue
        values = record.get(section)
        if not isinstance(values, list):
            continue

        row = {"entity_key": entity_key}
        for idx, column in enumerate(columns):
            row[str(column)] = values[idx] if idx < len(values) else None
        rows.append(row)

    return rows


def _pick_primary_metric(rows: list[dict[str, Any]]) -> str | None:
    if not rows:
        return None

    candidates: list[tuple[int, str]] = []
    columns = [name for name in rows[0] if name != "entity_key"]
    for name in columns:
        parsed = [_coerce_number(row.get(name)) for row in rows]
        numeric_count = sum(value is not None for value in parsed)
        if numeric_count == 0:
            continue

        score = numeric_count
        lowered = name.lower()
        if any(hint in lowered for hint in NUMERIC_HINTS):
            score += len(rows)
        candidates.append((score, name))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]


def _pick_date_column(rows: list[dict[str, Any]]) -> str | None:
    if not rows:
        return None

    candidates: list[tuple[int, str]] = []
    columns = [name for name in rows[0] if name != "entity_key"]
    for name in columns:
        parsed = [_coerce_date(row.get(name)) for row in rows]
        count = sum(value is not None for value in parsed)
        if count == 0:
            continue

        score = count
        lowered = name.lower()
        if any(hint in lowered for hint in DATE_HINTS):
            score += len(rows)
        candidates.append((score, name))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]


def _build_summary_cards(rows: list[dict[str, Any]]) -> list[tuple[str, str]]:
    cards = [("Entities", str(len(rows)))]
    if not rows:
        return cards

    metric = _pick_primary_metric(rows)
    if metric:
        values = [_coerce_number(row.get(metric)) for row in rows]
        numeric = [value for value in values if value is not None]
        if numeric:
            cards.append((f"Top {_humanize(metric)}", _format_number(max(numeric))))
            cards.append((f"Total {_humanize(metric)}", _format_number(sum(numeric))))

    date_column = _pick_date_column(rows)
    if date_column:
        dates = [_coerce_date(row.get(date_column)) for row in rows]
        resolved = [value for value in dates if value is not None]
        if resolved:
            cards.append((f"Latest {_humanize(date_column)}", max(resolved).strftime("%Y-%m-%d")))

    return cards


def _build_highlights(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    metric = _pick_primary_metric(rows)
    if not metric:
        return []

    ranked: list[tuple[float, dict[str, Any]]] = []
    for row in rows:
        value = _coerce_number(row.get(metric))
        if value is None:
            continue
        ranked.append((value, row))

    ranked.sort(reverse=True, key=lambda item: item[0])
    highlights: list[dict[str, str]] = []
    for value, row in ranked[:5]:
        label = str(
            row.get("entity_key")
            or row.get("nseSymbol")
            or row.get("nsesymbol")
            or row.get("companyName")
            or row.get("nameOfTheCompany")
            or "Unknown"
        )
        highlights.append(
            {
                "label": label,
                "metric": _humanize(metric),
                "value": _format_number(value),
            }
        )

    return highlights


def _table_columns(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return []

    preferred = ["entity_key"]
    preferred.extend(
        [
            "nseSymbol",
            "nsesymbol",
            "nameOfTheCompany",
            "companyName",
            "issueType",
            "issue_type",
            "stage",
        ]
    )

    columns = list(rows[0].keys())
    ordered = [name for name in preferred if name in columns]
    ordered.extend(name for name in columns if name not in ordered)
    return ordered


def _render_table(rows: list[dict[str, Any]], section_id: str) -> str:
    if not rows:
        return "<p class='empty'>No rows found in this section.</p>"

    columns = _table_columns(rows)
    search_id = f"search-{section_id}"
    column_count = len(columns)
    head = "".join(f"<th>{html.escape(_humanize(name))}</th>" for name in columns)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{_html_cell(row.get(column))}</td>" for column in columns)
        search_blob = " ".join(_format_value(row.get(column)) for column in columns)
        body_rows.append(
            f"<tr data-search='{html.escape(search_blob.lower())}'>{cells}</tr>"
        )

    body = "".join(body_rows)
    return f"""
    <div class="table-toolbar">
      <label for="{search_id}">Filter</label>
      <input id="{search_id}" data-table-filter="{section_id}" type="search" placeholder="Search this section" />
    </div>
    <div class="table-wrap">
      <table id="{section_id}">
        <thead><tr>{head}</tr></thead>
        <tbody>{body}</tbody>
      </table>
    </div>
    <p class="table-note">{len(rows)} rows, {column_count} columns.</p>
    """


def _render_section(name: str, rows: list[dict[str, Any]]) -> str:
    section_id = _slugify(name)
    cards = "".join(
        f"<article class='card'><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></article>"
        for label, value in _build_summary_cards(rows)
    )
    highlights = _build_highlights(rows)
    highlight_items = "".join(
        "<li>"
        f"<strong>{html.escape(item['label'])}</strong>"
        f"<span>{html.escape(item['metric'])}: {html.escape(item['value'])}</span>"
        "</li>"
        for item in highlights
    )
    highlight_block = (
        f"<section class='highlights'><h3>Top entities</h3><ul>{highlight_items}</ul></section>"
        if highlight_items
        else ""
    )

    return f"""
    <section class="dataset-section" id="section-{section_id}">
      <div class="section-head">
        <div>
          <p class="eyebrow">Section</p>
          <h2>{html.escape(_humanize(name))}</h2>
        </div>
      </div>
      <div class="cards">{cards}</div>
      {highlight_block}
      {_render_table(rows, section_id)}
    </section>
    """


def render_json_payload(payload: dict[str, Any], source_name: str) -> str:
    sections = []
    metadata = payload.get("metadata", {})
    if isinstance(metadata, dict):
        for section_name in metadata:
            rows = _normalize_rows(payload, str(section_name))
            sections.append((str(section_name), rows))

    total_entities = len(payload.get("data", {})) if isinstance(payload.get("data"), dict) else 0
    nav = "".join(
        f"<a href='#section-{_slugify(name)}'>{html.escape(_humanize(name))}</a>"
        for name, _rows in sections
    )
    body = "".join(_render_section(name, rows) for name, rows in sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(source_name)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4efe6;
      --panel: rgba(255, 251, 245, 0.92);
      --ink: #1f1f1b;
      --muted: #6a675f;
      --line: rgba(60, 51, 40, 0.12);
      --accent: #a63f25;
      --accent-soft: rgba(166, 63, 37, 0.12);
      --shadow: 0 20px 60px rgba(57, 40, 22, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(166, 63, 37, 0.18), transparent 28%),
        linear-gradient(180deg, #efe4d4 0%, var(--bg) 35%, #f7f1e8 100%);
    }}
    a {{ color: inherit; }}
    .shell {{
      width: min(1400px, calc(100vw - 32px));
      margin: 24px auto 48px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(255,255,255,0.76), rgba(255, 244, 228, 0.92));
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 28px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }}
    .eyebrow {{
      margin: 0 0 8px;
      color: var(--accent);
      font-size: 0.8rem;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{
      margin-bottom: 12px;
      font-size: clamp(2rem, 4vw, 3.8rem);
      line-height: 0.95;
    }}
    .lede {{
      max-width: 70ch;
      color: var(--muted);
      font-size: 1.02rem;
      line-height: 1.6;
    }}
    .hero-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 18px;
    }}
    .pill {{
      background: var(--accent-soft);
      border: 1px solid rgba(166, 63, 37, 0.22);
      border-radius: 999px;
      padding: 10px 14px;
      font-size: 0.95rem;
    }}
    nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 20px 0 0;
    }}
    nav a {{
      text-decoration: none;
      padding: 10px 14px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.66);
    }}
    .dataset-section {{
      margin-top: 22px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 22px;
      box-shadow: var(--shadow);
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 18px 0;
    }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 14px;
      background: rgba(255,255,255,0.72);
    }}
    .card span {{
      display: block;
      color: var(--muted);
      font-size: 0.88rem;
      margin-bottom: 8px;
    }}
    .card strong {{
      font-size: 1.15rem;
    }}
    .highlights ul {{
      list-style: none;
      padding: 0;
      margin: 0 0 18px;
      display: grid;
      gap: 10px;
    }}
    .highlights li {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 12px 14px;
      border-radius: 16px;
      background: rgba(166, 63, 37, 0.06);
      border: 1px solid rgba(166, 63, 37, 0.1);
    }}
    .table-toolbar {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 14px 0 12px;
    }}
    .table-toolbar input {{
      width: min(360px, 100%);
      padding: 10px 12px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.9);
      color: var(--ink);
    }}
    .table-wrap {{
      overflow: auto;
      border-radius: 18px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.74);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 900px;
    }}
    th, td {{
      padding: 10px 12px;
      vertical-align: top;
      border-bottom: 1px solid var(--line);
      text-align: left;
      font-size: 0.95rem;
    }}
    th {{
      position: sticky;
      top: 0;
      background: #f6ede2;
      z-index: 1;
    }}
    td {{
      max-width: 360px;
      color: #312f2a;
      word-break: break-word;
    }}
    .table-note, .empty {{
      color: var(--muted);
      margin: 12px 0 0;
    }}
    @media (max-width: 720px) {{
      .shell {{ width: min(100vw - 20px, 1400px); }}
      .hero, .dataset-section {{ padding: 18px; border-radius: 20px; }}
      .highlights li {{ flex-direction: column; }}
      .table-toolbar {{ flex-direction: column; align-items: stretch; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">Further Issue Tracker</p>
      <h1>{html.escape(source_name)}</h1>
      <p class="lede">
        Rendered view of the normalized filing payload. Each section uses the JSON metadata
        columns to label rows from the entity map, so the raw `metadata/data` structure becomes
        directly scannable.
      </p>
      <div class="hero-meta">
        <span class="pill">{total_entities} entities</span>
        <span class="pill">{len(sections)} sections</span>
      </div>
      <nav>{nav}</nav>
    </section>
    {body}
  </main>
  <script>
    for (const input of document.querySelectorAll("[data-table-filter]")) {{
      input.addEventListener("input", (event) => {{
        const tableId = event.target.getAttribute("data-table-filter");
        const query = event.target.value.trim().toLowerCase();
        const rows = document.querySelectorAll(`#${{tableId}} tbody tr`);
        for (const row of rows) {{
          row.hidden = query && !row.dataset.search.includes(query);
        }}
      }});
    }}
  </script>
</body>
</html>
"""


def render_json_file(input_path: str | Path, output_path: str | Path | None = None) -> Path:
    source = Path(input_path)
    with source.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    if output_path is None:
        output = source.with_suffix(".html")
    else:
        output = Path(output_path)

    html_output = render_json_payload(payload, source.name)
    output.write_text(html_output, encoding="utf-8")
    logger.info("Rendered %s to %s", source, output)
    return output


def discover_root_json_files(root: str | Path = ".") -> list[Path]:
    root_path = Path(root)
    return sorted(
        path
        for path in root_path.glob("*.json")
        if path.is_file() and path.name.endswith("_data.json")
    )
