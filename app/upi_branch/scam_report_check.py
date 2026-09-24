import pandas as pd
from app.upi_branch.merchant_verification import extract_upi_id

SCAM_REPORTS_PATH = "data/scam_reports.csv"

try:
    scam_reports_db = pd.read_csv(SCAM_REPORTS_PATH)
except FileNotFoundError:
    scam_reports_db = pd.DataFrame(columns=["upi_id", "report_count", "report_status", "last_reported"])


def check_scam_reports(payload: str) -> dict:
    """
    Checks whether the UPI ID in the payload has been reported
    as a scam by the community.

    Returns:
        dict: {
            "upi_id": str,
            "reported": bool,
            "report_count": int,
            "report_status": str or None,  # "Confirmed Scam" / "Under Investigation" / "Reported - Unverified"
            "last_reported": str or None
        }
    """
    upi_id = extract_upi_id(payload)

    if not upi_id:
        return {"upi_id": None, "reported": False, "report_count": 0, "report_status": None, "last_reported": None}

    match = scam_reports_db[scam_reports_db["upi_id"] == upi_id]

    if not match.empty:
        return {
            "upi_id": upi_id,
            "reported": True,
            "report_count": int(match.iloc[0]["report_count"]),
            "report_status": match.iloc[0]["report_status"],
            "last_reported": match.iloc[0]["last_reported"]
        }
    else:
        return {
            "upi_id": upi_id,
            "reported": False,
            "report_count": 0,
            "report_status": None,
            "last_reported": None
        }


