import pickle
import numpy as np
from urllib.parse import urlparse
import tensorflow as tf
load_model = tf.keras.models.load_model
import re


# ============================================================
# LOAD ALL 3 MODELS + SCALER + THRESHOLD
# ============================================================

try:

    with open("models/isolation_forest.pkl", "rb") as f:
        iso_forest = pickle.load(f)

    with open("models/one_class_svm.pkl", "rb") as f:
        oc_svm = pickle.load(f)

    # Autoencoder
    autoencoder = load_model("models/autoencoder.keras", compile=False)
    

    with open("models/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)

    with open("models/autoencoder_threshold.pkl", "rb") as f:
        ae_threshold = pickle.load(f)

    models_loaded = True

except FileNotFoundError:
    models_loaded = False


# ============================================================
# URL FEATURE EXTRACTION
# ============================================================

def extract_url_features(url: str) -> list:

    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    return [
        len(url),
        len(hostname),
        url.count("."),
        url.count("-"),
        url.count("@"),
        url.count("//") - 1 if url.count("//") > 0 else 0,
        1 if re.search(
            r"\d+\.\d+\.\d+\.\d+",
            hostname
        ) else 0,
        len(parsed.path),
        len(parsed.query),
        1 if parsed.scheme == "https" else 0,
        sum(c.isdigit() for c in hostname),
    ]


# ============================================================
# ANOMALY DETECTION
# ============================================================

def detect_anomaly(url: str) -> dict:

    """
    Runs the URL through all 3 unsupervised models:

    1. Isolation Forest
    2. One-Class SVM
    3. Autoencoder

    Majority voting:
    2 or more anomalous predictions = anomalous
    """

    if not models_loaded:

        return {
            "is_anomalous": None,
            "reason": "Models not loaded"
        }

    try:

        # ----------------------------------------------------
        # Extract URL features
        # ----------------------------------------------------

        features = np.array(
            extract_url_features(url)
        ).reshape(1, -1)


        # ----------------------------------------------------
        # Scale features
        # ----------------------------------------------------

        features_scaled = scaler.transform(features)


        # ----------------------------------------------------
        # 1. Isolation Forest
        # -1 = anomaly
        # ----------------------------------------------------

        iso_pred = iso_forest.predict(features)[0]

        iso_anomalous = iso_pred == -1


        # ----------------------------------------------------
        # 2. One-Class SVM
        # -1 = anomaly
        # ----------------------------------------------------

        svm_pred = oc_svm.predict(features_scaled)[0]

        svm_anomalous = svm_pred == -1


        # ----------------------------------------------------
        # 3. Autoencoder
        # High reconstruction error = anomaly
        # ----------------------------------------------------

        reconstruction = autoencoder.predict(
            features_scaled,
            verbose=0
        )

        mse = np.mean(
            np.power(
                features_scaled - reconstruction,
                2
            )
        )

        ae_anomalous = mse > ae_threshold


        # ----------------------------------------------------
        # Majority Voting
        # ----------------------------------------------------

        votes = sum([
            iso_anomalous,
            svm_anomalous,
            ae_anomalous
        ])

        is_anomalous = votes >= 2


        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------
        print("URL:", url)
        print("Isolation Forest:", iso_anomalous)
        print("One-Class SVM:", svm_anomalous)
        print("Autoencoder:", ae_anomalous)
        print("Anomaly Votes:", votes)
        
        
        return {

            "isolation_forest": bool(
                iso_anomalous
            ),

            "one_class_svm": bool(
                svm_anomalous
            ),

            "autoencoder": bool(
                ae_anomalous
            ),

            "votes_anomalous": int(
                votes
            ),

            "is_anomalous": bool(
                is_anomalous
            )
        }


    except Exception as e:

        return {
            "is_anomalous": None,
            "reason": f"Error: {e}"
        }