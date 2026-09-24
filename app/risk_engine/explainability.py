def explain_risk_score(qr_type: str, signals: dict, risk_score: int) -> str:
    if qr_type == "UPI":
        return _explain_upi(signals)
    elif qr_type == "URL":
        return _explain_url(signals)
    else:
        return "This QR code could not be classified as a valid UPI or URL payload, which itself is treated as a high-risk indicator."


def _explain_upi(signals: dict) -> str:
    reasons = []

    merchant_check = signals.get("merchant_check", {})
    scam_check = signals.get("scam_report_check", {})
    location_check = signals.get("location_check", {})

    if merchant_check.get("registered") is False:
        reasons.append("the UPI ID is not found in the registered merchant database")
    elif merchant_check.get("registered") is True:
        reasons.append(f"the UPI ID belongs to a registered merchant ({merchant_check.get('merchant_name')})")

    if scam_check.get("reported"):
        status = scam_check.get("report_status")
        last_reported = scam_check.get("last_reported")
        reasons.append(f"this UPI ID has a community scam report with status '{status}' (last reported on {last_reported})")

    if location_check.get("applicable"):
        if location_check.get("match") is False:
            distance = location_check.get("distance_km")
            reasons.append(f"your scan location is {distance} km away from the merchant's registered address")
        elif location_check.get("match") is True:
            reasons.append("your scan location matches the merchant's registered address")

    if not reasons:
        reasons.append("no significant risk indicators were found for this UPI ID")

    return " and ".join(reasons).capitalize() + "."


def _explain_url(signals: dict) -> str:
    reasons = []

    ssl_check = signals.get("ssl_check", {})
    threat_intel = signals.get("threat_intel", {})
    anomaly = signals.get("anomaly_score", {})
    sandbox = signals.get("sandbox_result", {})

    if ssl_check.get("uses_https") is False:
        reasons.append("the site does not use HTTPS encryption")
    elif ssl_check.get("valid_certificate") is False:
        reasons.append("the site's SSL certificate is invalid or expired")

    if threat_intel.get("overall_flagged"):
        sb = threat_intel.get("safe_browsing", {})
        vt = threat_intel.get("virustotal", {})
        if sb.get("flagged"):
            reasons.append("this URL is flagged by Google Safe Browsing as a known threat")
        if vt.get("flagged"):
            malicious = vt.get("malicious_count", 0)
            total = vt.get("total_engines", 0)
            reasons.append(f"{malicious} out of {total} VirusTotal security engines flagged this URL as malicious")

    if anomaly.get("is_anomalous"):
        votes = anomaly.get("votes_anomalous", 0)
        reasons.append(f"{votes} out of 3 anomaly detection models identified this URL's structure as unusual compared to known safe URLs")

    if sandbox.get("triggered_download"):
        reasons.append("visiting this URL triggers an automatic file download")
    if sandbox.get("suspicious_scripts"):
        reasons.append("suspicious script patterns were found on the page")
    if sandbox.get("redirect_count", 0) >= 2:
        reasons.append(f"the URL redirects {sandbox.get('redirect_count')} times before reaching its final destination")

    if not reasons:
        reasons.append("no significant risk indicators were found for this URL")

    return " and ".join(reasons).capitalize() + "."

