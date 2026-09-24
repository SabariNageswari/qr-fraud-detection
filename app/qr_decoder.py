# app/qr_decoder.py

import cv2
import numpy as np


def decode_qr(qr_image_file):
    """
    Decodes a QR code from an uploaded image file using OpenCV's
    built-in QRCodeDetector (no external zbar dependency needed).

    Args:
        qr_image_file: file-like object (from Flask request.files["qr_image"])

    Returns:
        str: decoded payload string (UPI URI or URL), or None if no QR found
    """
    try:
        file_bytes = np.frombuffer(qr_image_file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            return None

        detector = cv2.QRCodeDetector()
        data, points, _ = detector.detectAndDecode(img)

        if not data:
            return None

        return data.strip()

    except Exception as e:
        print(f"QR decode error: {e}")
        return None
