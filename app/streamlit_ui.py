import streamlit as st
import streamlit.components.v1 as components
import requests
from streamlit_js_eval import get_geolocation
# 🟢 UPDATED IMPORT: Updated to import the new function
from alert.voice_alert import trigger_browser_voice_alert

API_URL = "http://127.0.0.1:5000/scan"


st.set_page_config(page_title="Multi-Layer AI-Based QR Fraud Detection", page_icon="🔍", layout="centered")

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 100%);
    }
    .title-box {
        background: linear-gradient(90deg, #4F46E5, #7C3AED);
        padding: 1.5rem 2rem;
        border-radius: 18px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25);
    }
    .title-icon {
        background: rgba(255,255,255,0.25);
        border-radius: 50%;
        width: 48px;
        height: 48px;
        min-width: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
    }
    .title-box h1 {
        color: white;
        font-size: 1.4rem;
        margin: 0;
        line-height: 1.3;
    }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #A5B4FC;
        border-radius: 14px;
        padding: 0.5rem;
        background-color: #F5F7FF;
    }
    .stButton > button {
        background: linear-gradient(90deg, #4F46E5, #7C3AED);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #4338CA, #6D28D9);
        color: white;

    }

    /* ---------- White QR Upload Box ---------- */

div[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    color: #1F2937 !important;
    border: 2px dashed #A5B4FC !important;
    border-radius: 14px !important;
    padding: 0.5rem !important;
}

div[data-testid="stFileUploader"] section {
    background: #FFFFFF !important;
    color: #1F2937 !important;
}

div[data-testid="stFileUploader"] button {
    background: #FFFFFF !important;
    color: #1F2937 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
}

div[data-testid="stFileUploader"] button:hover {
    background: #F8FAFC !important;
    color: #111827 !important;
    border-color: #94A3B8 !important;
}

div[data-testid="stFileUploader"] label {
    color: #1F2937 !important;
}

div[data-testid="stFileUploader"] small {
    color: #64748B !important;
}
    .result-card {
        border-radius: 18px;
        padding: 1.8rem;
        margin-top: 0.5rem;
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 14px rgba(0,0,0,0.06);
    }
    .qr-type-row {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-weight: 700;
        color: #1F2937;
        font-size: 1.05rem;
        margin-bottom: 0.8rem;
    }
    .score-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.5rem 1.1rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }

    /* ---------- Risk score ring + summary box ---------- */
    .info-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.2rem;
        flex-wrap: wrap;
    }

    .gauge-box {
        width: 210px;
        min-width: 210px;
        background: linear-gradient(145deg, #F7FFFC, #F8FAFC);
        border: 1px solid #D9F5E8;
        border-radius: 16px;
        padding: 1.1rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
    }

    .gauge-title {
        font-size: 1rem;
        font-weight: 700;
        color: #475569;
        margin-bottom: 0.7rem;
    }

    .score-ring {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.8rem;
        transform: rotate(-90deg);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .score-ring-inner {
        width: 116px;
        height: 116px;
        border-radius: 50%;
        background: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        transform: rotate(90deg);
        box-shadow: inset 0 0 0 1px #EEF2F7;
    }

    .score-number {
        font-size: 2.1rem;
        font-weight: 800;
        line-height: 1;
        white-space: nowrap;
    }

    .score-number .score-max {
        font-size: 1rem;
        font-weight: 700;
        color: #64748B;
        margin-left: 2px;
    }

    .risk-tag {
        padding: 0.28rem 0.9rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
    }

    .summary-box {
        flex: 1;
        min-width: 260px;
        border-radius: 16px;
        padding: 1.35rem;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .summary-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 800;
        font-size: 1.35rem;
        margin-bottom: 0.55rem;
    }

    .summary-text {
        font-size: 1rem;
        line-height: 1.65;
        margin: 0;
    }

    /* ---------- Why this result ---------- */
    .why-heading {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.05rem;
        font-weight: 700;
        color: #4F46E5;
        margin: 0.4rem 0 0.6rem 0;
    }
    .why-box {
        background: #F5F3FF;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        font-size: 0.92rem;
        color: #374151;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

if "view" not in st.session_state:
    st.session_state.view = "scan"
if "result" not in st.session_state:
    st.session_state.result = None


def go_to_scan():
    st.session_state.view = "scan"
    st.session_state.result = None


STATUS_STYLES = {
    "Safe":       {"emoji": "✅", "accent": "#16A34A", "pill_bg": "#DCFCE7", "pill_text": "#166534",
                    "summary_bg": "#ECFDF5", "summary": "This QR code appears to be safe and does not show signs of fraudulent activity.",
                    "tag": "Low Risk"},
    "Suspicious": {"emoji": "⚠️", "accent": "#D97706", "pill_bg": "#FEF3C7", "pill_text": "#92400E",
                    "summary_bg": "#FFFBEB", "summary": "This QR code shows some risk indicators. Proceed with caution.",
                    "tag": "Medium Risk"},
    "Fraudulent": {"emoji": "🚨", "accent": "#DC2626", "pill_bg": "#FEE2E2", "pill_text": "#991B1B",
                    "summary_bg": "#FEF2F2", "summary": "This QR code has been identified as fraudulent. Do not proceed.",
                    "tag": "High Risk"},
}

TITLE_HTML = """
<div class="title-box">
    <div class="title-icon">🛡️</div>
    <h1>Multi-Layer AI-Based QR Code Fraud Detection and Risk Analysis</h1>
</div>
"""

# ============================================================
# SCAN PAGE
# ============================================================
if st.session_state.view == "scan":

    st.markdown(TITLE_HTML, unsafe_allow_html=True)

    location = get_geolocation()
    user_lat, user_lng = None, None
    if location:
        user_lat = location["coords"]["latitude"]
        user_lng = location["coords"]["longitude"]

    qr_image = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg"])

    if qr_image is not None:
        st.image(qr_image, caption="QR Code", width=220)

        if st.button("🔍 Analyze QR Code"):
            with st.spinner("Analyzing QR code..."):
                try:
                    files = {"qr_image": qr_image}
                    data = {}
                    if user_lat is not None and user_lng is not None:
                        data["user_lat"] = user_lat
                        data["user_lng"] = user_lng

                    response = requests.post(API_URL, files=files, data=data)
                    result = response.json()

                    st.session_state.result = result
                    st.session_state.view = "result"
                    st.rerun()

                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to backend. Make sure Flask server is running (python -m app.main).")

# ============================================================
# RESULT PAGE
# ============================================================
else:
    result = st.session_state.result

    st.markdown(TITLE_HTML, unsafe_allow_html=True)

    if result and "error" in result:
        st.error(result["error"])
        st.button("⬅ Scan Another QR Code", on_click=go_to_scan)
    elif result:
        risk_label = result.get("risk_label", "Suspicious")

        # Read the REAL score returned by Flask.
        try:
            raw_score = result.get("risk_score")
            risk_score = float(raw_score) if raw_score is not None else 0.0
        except (TypeError, ValueError):
            risk_score = 0.0

        risk_score = max(0.0, min(risk_score, 100.0))

        qr_type = result.get("qr_type", "Unknown")
        explanation = result.get("explanation", "No explanation available.")
        style = STATUS_STYLES.get(risk_label, STATUS_STYLES["Suspicious"])
        type_icon = "🔗" if qr_type == "URL" else "💳"

        score_angle = risk_score * 3.6

        gauge_color = {
            "Safe": "#22C55E",
            "Suspicious": "#F59E0B",
            "Fraudulent": "#EF4444"
        }.get(risk_label, "#F59E0B")

        st.markdown(
            f'<div class="qr-type-row">{type_icon} <b>QR Type:</b>&nbsp; {qr_type}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'''
            <div class="score-tag"
                 style="background:{style["pill_bg"]}; color:{style["pill_text"]};">
                {style["emoji"]} <b>Status: {risk_label}</b>
            </div>
            ''',
            unsafe_allow_html=True
        )

        # Render the score card with components.html so Streamlit
        # renders the HTML instead of displaying the tags as text.
        score_card_html = f"""
        <style>
            * {{
                box-sizing: border-box;
                font-family: Arial, sans-serif;
            }}
            body {{
                margin: 0;
                padding: 0;
                background: transparent;
            }}
            .info-row {{
                display: flex;
                gap: 16px;
                width: 100%;
                align-items: stretch;
            }}
            .gauge-box {{
                width: 42%;
                min-width: 210px;
                min-height: 260px;
                background: linear-gradient(145deg, #F7FFFC, #F8FAFC);
                border: 1px solid #D9F5E8;
                border-radius: 16px;
                padding: 16px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }}
            .gauge-title {{
                font-size: 16px;
                font-weight: 700;
                color: #475569;
                margin-bottom: 12px;
            }}
            .score-ring {{
                width: 170px;
                height: 170px;
                border-radius: 50%;
                background: conic-gradient(
                    {gauge_color} 0deg,
                    {gauge_color} {score_angle}deg,
                    #E5EAF2 {score_angle}deg,
                    #E5EAF2 360deg
                );
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 12px;
            }}
            .score-ring-inner {{
                width: 132px;
                height: 132px;
                border-radius: 50%;
                background: #FFFFFF;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .score-number {{
                font-size: 38px;
                font-weight: 800;
                line-height: 1;
                color: {gauge_color};
                white-space: nowrap;
            }}
            .score-max {{
                font-size: 18px;
                font-weight: 700;
                color: #64748B;
                margin-left: 3px;
            }}
            .risk-tag {{
                padding: 6px 16px;
                border-radius: 999px;
                font-size: 13px;
                font-weight: 700;
                background: {style["pill_bg"]};
                color: {style["pill_text"]};
            }}
            .summary-box {{
                flex: 1;
                min-height: 260px;
                background: {style["summary_bg"]};
                border: 1px solid {style["accent"]}30;
                border-radius: 16px;
                padding: 28px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }}
            .summary-title {{
                color: {style["accent"]};
                font-size: 28px;
                font-weight: 800;
                margin-bottom: 12px;
            }}
            .summary-text {{
                color: {style["pill_text"]};
                font-size: 18px;
                line-height: 1.65;
                margin: 0;
            }}
            @media (max-width: 650px) {{
                .info-row {{
                    flex-direction: column;
                }}
                .gauge-box,
                .summary-box {{
                    width: 100%;
                    min-width: 0;
                }}
            }}
        </style>

        <div class="info-row">
            <div class="gauge-box">
                <div class="gauge-title">Risk Score</div>

                <div class="score-ring">
                    <div class="score-ring-inner">
                        <div class="score-number">
                            {risk_score:.0f}<span class="score-max">/100</span>
                        </div>
                    </div>
                </div>

                <div class="risk-tag">{style["tag"]}</div>
            </div>

            <div class="summary-box">
                <div class="summary-title">
                    {style["emoji"]} {risk_label}
                </div>

                <p class="summary-text">
                    {style["summary"]}
                </p>
            </div>
        </div>
        """

        components.html(score_card_html, height=285, scrolling=False)

        st.markdown(
            f'''
            <div class="why-heading">ℹ️ Why this result?</div>
            <div class="why-box">{explanation}</div>
            ''',
            unsafe_allow_html=True
        )

        # 🟢 UPDATED VOICE ALERT FUNCTION CALL:
        trigger_browser_voice_alert(risk_label)

        st.write("")
        st.button("🔄 Scan Next QR Code", on_click=go_to_scan)