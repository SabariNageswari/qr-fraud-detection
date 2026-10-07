def classify_qr(payload: str) -> str:
    """
    Classifies the decoded QR payload as UPI, URL, or UNKNOWN.
    """

    if not payload:
        return "UNKNOWN"

    cleaned = payload.strip().lower()

    # UPI QR
    if cleaned.startswith("upi://"):
        return "UPI"

    # Normal URLs
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        return "URL"

    # Domain-style URLs without http/https
    if (
        cleaned.startswith("www.")
        or "." in cleaned
        and " " not in cleaned
        and not cleaned.startswith("upi:")
    ):
        return "URL"

    return "UNKNOWN"
