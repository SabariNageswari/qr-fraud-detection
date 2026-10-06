# app/alert/voice_alert.py
import streamlit.components.v1 as components


def trigger_browser_voice_alert(risk_label: str):
    """
    Browser-ல் Fraudulent QR Code-க்கு மட்டும் voice alert பேச வைக்கும்.
    """

    # Safe / Suspicious என்றால் எந்த voice-ம் வராது
    if risk_label != "Fraudulent":
        return

    voice_config = {
        "Fraudulent": {
            "message": "Danger. This QR code is fraudulent. Do not proceed.",
            "rate": 1.1,
            "pitch": 0.7,
        }
    }

    config = voice_config["Fraudulent"]

    clean_message = config["message"].replace("'", "\\'")

    # HTML & JS Component injection
    js_code = f"""
    <script>
    (function() {{
        if (!("speechSynthesis" in window)) return;

        window.speechSynthesis.cancel();

        const msg = new SpeechSynthesisUtterance('{clean_message}');
        msg.rate = {config["rate"]};
        msg.pitch = {config["pitch"]};
        msg.volume = 1;

        function play() {{
            const voices = window.speechSynthesis.getVoices();

            if (voices.length > 0) {{
                const preferred =
                    voices.find(v => /en[-_]IN/i.test(v.lang)) ||
                    voices.find(v => /^en/i.test(v.lang));

                if (preferred) {{
                    msg.voice = preferred;
                }}
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

    # Invisible JavaScript execution
    components.html(js_code, height=0, width=0)
    
