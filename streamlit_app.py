import subprocess
import time
import streamlit as st


@st.cache_resource
def start_flask_backend():
    process = subprocess.Popen(
        [
            "gunicorn",
            "--bind",
            "127.0.0.1:5000",
            "app.main:app"
        ]
    )

    time.sleep(5)

    return process


# Start Flask backend
start_flask_backend()


# Start your existing Streamlit UI
exec(
    open("app/streamlit_ui.py", encoding="utf-8").read(),
    globals()
)
