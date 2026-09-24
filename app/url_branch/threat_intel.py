import os
import requests

GOOGLE_SAFE_BROWSING_KEY = os.getenv("GOOGLE_SAFE_BROWSING_KEY")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

SAFE_BROWSING_URL = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_SAFE_BROWSING_KEY}"
VIRUSTOTAL_URL_SCAN = "https://www.virustotal.com/api/v3/urls"


def check_google_safe_browsing(url: str) -> dict:
    """
    Checks a URL against Google Safe Browsing's list of known threats.

    Returns:
        dict: {"flagged": bool, "threat_types": list}
    """
    payload = {
        "client": {"clientId": "qr-fraud-detector", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        response = requests.post(SAFE_BROWSING_URL, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "matches" in data:
            threat_types = [match["threatType"] for match in data["matches"]]
            return {"flagged": True, "threat_types": threat_types}
        else:
            return {"flagged": False, "threat_types": []}

    except requests.exceptions.RequestException as e:
        print(f"Safe Browsing API error: {e}")
        return {"flagged": None, "threat_types": [], "error": str(e)}


def check_virustotal(url: str) -> dict:
    """
    Submits a URL to VirusTotal and retrieves the analysis results
    from multiple antivirus/security engines.

    Returns:
        dict: {"flagged": bool, "malicious_count": int, "total_engines": int}
    """
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}

    try:
        # Step 1: Submit the URL for scanning
        submit_response = requests.post(
            VIRUSTOTAL_URL_SCAN,
            headers=headers,
            data={"url": url},
            timeout=5
        )
        submit_response.raise_for_status()
        analysis_id = submit_response.json()["data"]["id"]

        # Step 2: Fetch the analysis result
        analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        result_response = requests.get(analysis_url, headers=headers, timeout=5)
        result_response.raise_for_status()
        result_data = result_response.json()

        stats = result_data["data"]["attributes"]["stats"]
        malicious_count = stats.get("malicious", 0)
        suspicious_count = stats.get("suspicious", 0)
        total_engines = sum(stats.values())

        flagged = (malicious_count + suspicious_count) > 0

        return {
            "flagged": flagged,
            "malicious_count": malicious_count,
            "suspicious_count": suspicious_count,
            "total_engines": total_engines
        }

    except requests.exceptions.RequestException as e:
        print(f"VirusTotal API error: {e}")
        return {"flagged": None, "malicious_count": 0, "total_engines": 0, "error": str(e)}


def check_threat_intelligence(url: str) -> dict:
    """
    Combines Google Safe Browsing and VirusTotal results into a
    single threat intelligence signal.

    Returns:
        dict: {
            "safe_browsing": dict,
            "virustotal": dict,
            "overall_flagged": bool
        }
    """
    safe_browsing_result = check_google_safe_browsing(url)
    virustotal_result = check_virustotal(url)

    overall_flagged = bool(
        safe_browsing_result.get("flagged") or virustotal_result.get("flagged")
    )

    return {
        "safe_browsing": safe_browsing_result,
        "virustotal": virustotal_result,
        "overall_flagged": overall_flagged
    }

