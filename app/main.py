import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load API keys from config/api_keys.env
load_dotenv("config/api_keys.env")

from app.qr_decoder import decode_qr
from app.classifier import classify_qr

# UPI branch imports
from app.upi_branch.merchant_verification import verify_merchant
from app.upi_branch.scam_report_check import check_scam_reports
from app.upi_branch.location_verification import verify_location

# URL branch imports
from app.url_branch.ssl_certificate_check import check_ssl_certificate
from app.url_branch.threat_intel import check_threat_intelligence
from app.url_branch.zero_day_model import detect_anomaly
from app.url_branch.sandbox_analysis import run_sandbox_analysis

# Risk engine imports
from app.risk_engine.risk_score import calculate_risk_score
from app.risk_engine.explainability import explain_risk_score

app = Flask(__name__)
CORS(app)  # 🟢 Added CORS to allow requests from Streamlit frontend

# Load merchant database safely at startup
try:
    merchant_db = pd.read_csv("data/merchant_database.csv")
except Exception as e:
    print(f"Warning: Could not load merchant database: {e}")
    merchant_db = pd.DataFrame()


@app.route("/scan", methods=["POST"])
def scan_qr():
    """
    Main pipeline: receives an uploaded QR image (+ optional user GPS
    coordinates), decodes it, classifies it, runs the correct branch,
    scores the risk, and explains it. Voice alerting happens on the
    frontend (Streamlit), not here.
    """
    if "qr_image" not in request.files:
        return jsonify({"error": "No QR image provided"}), 400

    qr_image = request.files["qr_image"]

    # Optional GPS coordinates sent from the frontend (Streamlit)
    user_lat = request.form.get("user_lat", type=float)
    user_lng = request.form.get("user_lng", type=float)

    # Step 1: Decode QR
    payload = decode_qr(qr_image)
    if payload is None:
        return jsonify({"error": "Could not decode QR code"}), 400

    # Step 2: Classify payload type
    qr_type = classify_qr(payload)

    signals = {}

    # Step 3: Branch-specific analysis
    if qr_type == "UPI":
        merchant_result = verify_merchant(payload)
        signals["merchant_check"] = merchant_result
        signals["scam_report_check"] = check_scam_reports(payload)

        # Determine if this merchant is a fixed shop (from merchant DB)
        is_fixed_shop = False
        if merchant_result.get("upi_id") and not merchant_db.empty:
            match = merchant_db[merchant_db["upi_id"] == merchant_result["upi_id"]]
            if not match.empty and "shop_type" in match.columns:
                is_fixed_shop = match.iloc[0]["shop_type"] == "fixed"

        signals["location_check"] = verify_location(
            payload,
            merchant_db=merchant_db,
            user_lat=user_lat,
            user_lng=user_lng,
            is_fixed_shop=is_fixed_shop
        )

    elif qr_type == "URL":
        signals["ssl_check"] = check_ssl_certificate(payload)
        signals["threat_intel"] = check_threat_intelligence(payload)
        signals["anomaly_score"] = detect_anomaly(payload)
        signals["sandbox_result"] = run_sandbox_analysis(payload)

    else:
        return jsonify({"error": "Unsupported or malformed QR code"}), 400

    # Step 4: Composite risk scoring
    risk_score, risk_label = calculate_risk_score(qr_type, signals)

    print("DEBUG RISK SCORE:", risk_score)
    print("DEBUG RISK LABEL:", risk_label)

    # Step 5: Explainability
    explanation = explain_risk_score(qr_type, signals, risk_score)

    # Step 6: Return result (frontend handles voice alert)
    return jsonify({
        "qr_type": qr_type,
        "risk_score": risk_score,
        "risk_label": risk_label,
        "explanation": explanation
    })


if __name__ == "__main__":
    # 🟢 Set explicit port and host for backend execution
    app.run(host="0.0.0.0", port=5000, debug=True)