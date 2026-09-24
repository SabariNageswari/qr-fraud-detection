import os
import pandas as pd
import numpy as np
import pickle
from urllib.parse import urlparse
import re

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import tensorflow as tf

Model = tf.keras.Model
Input = tf.keras.Input
Dense = tf.keras.layers.Dense

# Ensure the models/ folder exists
os.makedirs("models", exist_ok=True)


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
        1 if re.search(r"\d+\.\d+\.\d+\.\d+", hostname) else 0,
        len(parsed.path),
        len(parsed.query),
        1 if parsed.scheme == "https" else 0,
        sum(c.isdigit() for c in hostname),
    ]


# Load safe URLs dataset
safe_urls = pd.read_csv("data/safe_urls.csv")
X = np.array(safe_urls["url"].apply(extract_url_features).tolist())

# Scale features (important for SVM and Autoencoder)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- 1. Isolation Forest ---
iso_forest = IsolationForest(contamination=0.05, random_state=42)
iso_forest.fit(X)
with open("models/isolation_forest.pkl", "wb") as f:
    pickle.dump(iso_forest, f)

# --- 2. One-Class SVM ---
oc_svm = OneClassSVM(kernel="rbf", nu=0.05, gamma="scale")
oc_svm.fit(X_scaled)
with open("models/one_class_svm.pkl", "wb") as f:
    pickle.dump(oc_svm, f)

# --- 3. Autoencoder ---
input_dim = X_scaled.shape[1]
input_layer = Input(shape=(input_dim,))
encoded = Dense(6, activation="relu")(input_layer)
encoded = Dense(3, activation="relu")(encoded)
decoded = Dense(6, activation="relu")(encoded)
decoded = Dense(input_dim, activation="linear")(decoded)

autoencoder = Model(inputs=input_layer, outputs=decoded)
autoencoder.compile(optimizer="adam", loss="mse")
autoencoder.fit(X_scaled, X_scaled, epochs=50, batch_size=16, verbose=0)
autoencoder.save("models/autoencoder.keras")

# Save scaler too — needed at inference time
with open("models/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

# Save reconstruction error threshold (95th percentile of training errors)
reconstructions = autoencoder.predict(X_scaled)
mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
threshold = np.percentile(mse, 95)
with open("models/autoencoder_threshold.pkl", "wb") as f:
    pickle.dump(threshold, f)

print("All 3 models trained and saved.")

