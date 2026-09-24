def classify_qr(payload: str) -> str:
    """
    Classifies the decoded QR payload as UPI, URL, or UNKNOWN.

    Args:
        payload (str): decoded string from the QR code

    Returns:
        str: "UPI", "URL", or "UNKNOWN"
    """
    if not payload:
        return "UNKNOWN"

    cleaned = payload.strip().lower()

    if cleaned.startswith("upi://"):
        return "UPI"
    elif cleaned.startswith("http://") or cleaned.startswith("https://"):
        return "URL"
    else:
        return "UNKNOWN"