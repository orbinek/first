import pdfplumber
import uuid
import re
from decimal import Decimal
from datetime import datetime
from app.services.sector_mapping import SECTOR_MAP


def _parse_decimal(value: str | None) -> Decimal | None:
    if not value:
        return None
    return Decimal(value.replace(".", "").replace(",", "."))


def _extract_snapshot_metadata(text: str) -> dict:
    print("=== FIRST PAGE TEXT ===")
    print(text)
    print("=== END FIRST PAGE TEXT ===")

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # Snapshot date
    date_match = re.search(
        r"Období od \d{2}\.\d{2}\.\d{4} do (\d{2}\.\d{2}\.\d{4})",
        text,
    )

    snapshot_date = (
        datetime.strptime(date_match.group(1), "%d.%m.%Y").date()
        if date_match
        else None
    )

    account_currency = None
    reported_cash = None
    reported_account_value = None

    for line in lines:
        if re.search(r"\b(CZK|EUR|USD)\b", line) and re.search(r"\d+\.\d+", line):
            parts = line.split()
            try:
                account_currency = parts[3]
                reported_cash = _parse_decimal(parts[4])
                reported_account_value = _parse_decimal(parts[5])
            except (IndexError, ValueError):
                pass
            break

    return {
        "snapshot_date": snapshot_date,
        "account_currency": account_currency,
        "reported_cash": reported_cash,
        "reported_account_value": reported_account_value,
    }


ROW_REGEX = re.compile(
    r"""
    ^\d+\s+
    (?P<symbol>\S+)\s+
    (?P<name>.+?)\s+
    (?P<isin>[A-Z0-9]{12})\s+
    (?P<asset_class>Cash Stocks|ETFs|ETN|ETC)\s+
    (?P<value>[\d.,]+)\s+
    (?P<currency>[A-Z]{3})\s+
    (?P<quantity>[\d.,]+)
    $
    """,
    re.VERBOSE,
)


def _extract_positions_from_text(text: str, is_fractional: bool):
    positions = []

    for line in text.splitlines():
        line = line.strip()

        # Skip obvious noise
        if not line:
            continue
        if line.startswith("Číslo "):
            continue
        if line.startswith("Stav na konci dne"):
            continue

        match = ROW_REGEX.match(line)
        if not match:
            continue

        data = match.groupdict()
        symbol = data["symbol"]

        positions.append({
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "name": data["name"],
            "isin": data["isin"],
            "asset_class": data["asset_class"],
            "sector": SECTOR_MAP.get(symbol.split(".")[0], "Unknown"),
            "reported_market_value": _parse_decimal(data["value"]),
            "currency": data["currency"],
            "quantity": _parse_decimal(data["quantity"]),
            "is_fractional": is_fractional,
        })

    return positions


def parse_xtb_pdf(path: str) -> dict:
    positions = []

    with pdfplumber.open(path) as pdf:
        first_page_text = pdf.pages[0].extract_text() or ""
        metadata = _extract_snapshot_metadata(first_page_text)

        for page in pdf.pages:
            text = page.extract_text() or ""

            if "Nástroje OMI" in text:
                positions.extend(
                    _extract_positions_from_text(text, is_fractional=False)
                )

            if "Frakční práva" in text:
                positions.extend(
                    _extract_positions_from_text(text, is_fractional=True)
                )

    return {
        **metadata,
        "positions": positions,
    }
