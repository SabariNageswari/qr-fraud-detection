# app/alert/voice_alert.py
import streamlit.components.v1 as components

def trigger_browser_voice_alert(risk_label: str):
    """
    Streamlit Frontend-ல் பயனர் பிரவுசரிலேயே Voice Alert பேச வைக்கும் ஃபங்ஷன்.
    Autoplay block ஆகாமல் இருக்க Custom HTML/JS Inject செய்கிறது.
    """
    voice_config = {
        "Safe": {
            "message": "This QR code appears safe to proceed.",
            "rate": 0.95,
            "pitch": 1.1,
        },
        "Suspicious": {
            "message": "Warning. This QR code looks suspicious.",
            "rate": 1.0,
            "pitch": 0.9,
        },
        "Fraudulent": {
            "message": "Danger. This QR code is fraudulent. Do not proceed.",
            "rate": 1.1,
            "pitch": 0.7,
        },
    }

    config = voice_config.get(
        risk_label,
        {
            "message": "Unable to determine the safety of this QR code.",
            "rate": 1.0,
            "pitch": 1.0,
        },
    )

    clean_message = config["message"].replace("'", "\\'")

    # HTML & JS Component injection
    js_code = f"""
    <script>
    (function() {{
        if (!("speechSynthesis" in window)) return;

        window.speechSynthesis.cancel(); // பழைய ஆடியோவை நிறுத்துதல்

        const msg = new SpeechSynthesisUtterance('{clean_message}');
        msg.rate = {config["rate"]};
        msg.pitch = {config["pitch"]};
        msg.volume = 1;

        function play() {{
            const voices = window.speechSynthesis.getVoices();
            if (voices.length > 0) {{
                const preferred = voices.find(v => /en[-_]IN/i.test(v.lang)) ||
                                  voices.find(v => /^en/i.test(v.lang));
                if (preferred) msg.voice = preferred;
            }}
            window.speechSynthesis.speak(msg);
        }}

        if (window.speechSynthesis.getVoices().length > 0) {{
            play();
        }} else {{
                window.speechSynthesis.onvoiceschanged = function() {{
                window.speechSynthesis.onvoiceschanged = null;
                play();
            }};
        }}
    }})();
    </script>
    """
    
    # Streamlit UI-க்குள் மறைமுகமாக (Invisible) இந்த JS-ஐ ரன் செய்தல்
    components.html(js_code, height=0, width=0)