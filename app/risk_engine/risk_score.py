def calculate_risk_score(qr_type: str, signals: dict) -> tuple:
    if qr_type == "UPI":
        return _score_upi(signals)
    elif qr_type == "URL":
        return _score_url(signals)
    else:
        return 100, "Fraudulent"


def _score_upi(signals: dict) -> tuple:
    score = 0

    merchant_check = signals.get("merchant_check", {})
    scam_check = signals.get("scam_report_check", {})
    location_check = signals.get("location_check", {})

    # 1. Merchant not registered → high risk
    if merchant_check.get("registered") is False:
        score += 35

    # 2. Scam reports → weight depends on report_status
    report_status = scam_check.get("report_status")
    if scam_check.get("reported"):
        status_weights = {
            "Confirmed Scam": 40,
            "Under Investigation": 20,
            "Reported - Unverified": 10
        }
        score += status_weights.get(report_status, 15)

    # 3. Location mismatch (only applicable for fixed shops)
    if location_check.get("applicable") and location_check.get("match") is False:
        score += 25

    # 4. A "Confirmed Scam" report is decisive on its own — force at
    # least the "Fraudulent" threshold even if the merchant is
    # registered (a registered identity can still be compromised
    # or misused for fraud).
    if report_status == "Confirmed Scam":
        score = max(score, 60)

    score = min(score, 100)
    label = _classify_score(score)
    return score, label


def _score_url(signals: dict) -> tuple:
    score = 0

    ssl_check = signals.get("ssl_check", {})
    threat_intel = signals.get("threat_intel", {})
    anomaly = signals.get("anomaly_score", {})
    sandbox = signals.get("sandbox_result", {})

    if ssl_check.get("uses_https") is False:
        score += 15
    elif ssl_check.get("valid_certificate") is False:
        score += 25

    if threat_intel.get("overall_flagged"):
        score += 40

    if anomaly.get("is_anomalous"):
        votes = anomaly.get("votes_anomalous", 0)
        score += 10 + (votes * 5)

    if sandbox.get("triggered_download"):
        score += 20
    if sandbox.get("suspicious_scripts"):
        score += 15
    if sandbox.get("redirect_count", 0) >= 2:
        score += 10
    if sandbox.get("load_error"):
        score += 5

    score = min(score, 100)
    label = _classify_score(score)
    return score, label


def _classify_score(score: int) -> str:
    if score < 30:
        return "Safe"
    elif score < 60:
        return "Suspicious"
    else:
        return "Fraudulent"
