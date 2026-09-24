"""
End-to-end tests for the QR fraud detection pipeline.
Run with: pytest tests/test_pipeline.py -v
(Run from inside the app/ folder, or add app/ to your PYTHONPATH,
since these modules use relative imports like the rest of the app.)
"""

import sys
import os

# Allow imports from the app/ folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from classifier import classify_qr
from url_branch.ssl_certificate_check import check_ssl_certificate
from risk_engine.risk_score import calculate_risk_score
from risk_engine.explainability import explain_risk_score


# ---------- classifier.py tests ----------

def test_classify_upi_payload():
    payload = "upi://pay?pa=shop123@okaxis&pn=TestShop&am=100&cu=INR"
    assert classify_qr(payload) == "UPI"


def test_classify_url_payload():
    payload = "https://example.com"
    assert classify_qr(payload) == "URL"


def test_classify_unknown_payload():
    payload = "just some random text"
    assert classify_qr(payload) == "UNKNOWN"


def test_classify_empty_payload():
    assert classify_qr("") == "UNKNOWN"
    assert classify_qr(None) == "UNKNOWN"


# ---------- ssl_certificate_check.py tests ----------

def test_ssl_check_no_https():
    result = check_ssl_certificate("http://example.com")
    assert result["uses_https"] is False
    assert result["reason"] == "URL does not use HTTPS"


def test_ssl_check_valid_https_site():
    # example.com has a valid, well-known certificate — safe to test live
    result = check_ssl_certificate("https://example.com")
    assert result["uses_https"] is True
    assert result["valid_certificate"] is True


# ---------- risk_scoring.py tests ----------

def test_risk_score_safe_url():
    signals = {
        "ssl_check": {"uses_https": True, "valid_certificate": True},
        "threat_intel": {"overall_flagged": False},
        "anomaly_score": {"is_anomalous": False, "votes_anomalous": 0},
        "sandbox_result": {
            "triggered_download": False,
            "suspicious_scripts": False,
            "redirect_count": 0,
            "load_error": None
        }
    }
    score, label = calculate_risk_score("URL", signals)
    assert label == "Safe"
    assert score < 30


def test_risk_score_fraudulent_url():
    signals = {
        "ssl_check": {"uses_https": False},
        "threat_intel": {"overall_flagged": True},
        "anomaly_score": {"is_anomalous": True, "votes_anomalous": 3},
        "sandbox_result": {
            "triggered_download": True,
            "suspicious_scripts": True,
            "redirect_count": 3,
            "load_error": None
        }
    }
    score, label = calculate_risk_score("URL", signals)
    assert label == "Fraudulent"
    assert score >= 60


def test_risk_score_safe_upi():
    signals = {
        "merchant_check": {"registered": True, "merchant_name": "Test Shop"},
        "scam_report_check": {"reported": False, "report_count": 0},
        "location_check": {"applicable": True, "match": True, "distance_km": 0.2}
    }
    score, label = calculate_risk_score("UPI", signals)
    assert label == "Safe"


def test_risk_score_fraudulent_upi():
    signals = {
        "merchant_check": {"registered": False, "merchant_name": None},
        "scam_report_check": {"reported": True, "report_count": 20},
        "location_check": {"applicable": True, "match": False, "distance_km": 15.0}
    }
    score, label = calculate_risk_score("UPI", signals)
    assert label == "Fraudulent"


def test_risk_score_unknown_qr_type():
    score, label = calculate_risk_score("UNKNOWN", {})
    assert label == "Fraudulent"
    assert score == 100


# ---------- explainability.py tests ----------

def test_explanation_mentions_scam_reports():
    signals = {
        "merchant_check": {"registered": True, "merchant_name": "Test Shop"},
        "scam_report_check": {"reported": True, "report_count": 5},
        "location_check": {"applicable": False, "match": None}
    }
    explanation = explain_risk_score("UPI", signals, 50)
    assert "reported" in explanation.lower()


def test_explanation_no_risk_found():
    signals = {
        "ssl_check": {"uses_https": True, "valid_certificate": True},
        "threat_intel": {"overall_flagged": False},
        "anomaly_score": {"is_anomalous": False},
        "sandbox_result": {}
    }
    explanation = explain_risk_score("URL", signals, 5)
    assert isinstance(explanation, str)
    assert len(explanation) > 0

