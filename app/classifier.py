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

    # URLs with protocol
    if cleaned.startswith(("http://", "https://")):
        return "URL"

    # URLs without protocol
    if cleaned.startswith("www."):
        return "URL"

    # Domain-style URL
    first_part = cleaned.split("/")[0]

    if "." in first_part and " " not in cleaned:
        return "URL"

    return "UNKNOWN"
