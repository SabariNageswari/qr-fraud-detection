import pandas as pd
from urllib.parse import urlparse, parse_qs

# Load merchant database once at module load time
MERCHANT_DB_PATH = "data/merchant_database.csv"

try:
    merchant_db = pd.read_csv(MERCHANT_DB_PATH)
except FileNotFoundError:
    merchant_db = pd.DataFrame(columns=["upi_id", "merchant_name", "registered"])


def extract_upi_id(payload: str) -> str:
    """
    Extracts the UPI ID (pa field) from a UPI payload string.
    Example payload: upi://pay?pa=merchant@upi&pn=MerchantName&am=500&cu=INR
    """
    # UPI payloads aren't standard URLs, so parse query params manually
    query_string = payload.split("?", 1)[-1] if "?" in payload else ""
    params = parse_qs(query_string)
    upi_id = params.get("pa", [None])[0]
    return upi_id


def verify_merchant(payload: str) -> dict:
    """
    Checks whether the UPI ID in the payload is a registered merchant
    in the merchant database.

    Returns:
        dict: {
            "upi_id": str,
            "registered": bool,
            "merchant_name": str or None
        }
    """
    upi_id = extract_upi_id(payload)

    if not upi_id:
        return {"upi_id": None, "registered": False, "merchant_name": None}

    match = merchant_db[merchant_db["upi_id"] == upi_id]

    if not match.empty:
        return {
            "upi_id": upi_id,
            "registered": True,
            "merchant_name": match.iloc[0]["merchant_name"]
        }
    else:
        return {
            "upi_id": upi_id,
            "registered": False,
            "merchant_name": None
        }
