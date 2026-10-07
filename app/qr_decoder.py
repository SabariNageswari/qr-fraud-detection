# app/qr_decoder.py

import cv2
import numpy as np


def decode_qr(qr_image_file):
    """
    Decode QR code from uploaded image using multiple OpenCV
    preprocessing methods.
    """

    try:
        # Read uploaded image only once
        file_bytes = np.frombuffer(qr_image_file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            return None

        detector = cv2.QRCodeDetector()

        # Different image versions to improve QR detection
        images_to_try = []

        # 1. Original image
        images_to_try.append(img)

        # 2. Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        images_to_try.append(gray)

        # 3. Enlarged image
        height, width = gray.shape[:2]

        if width < 1000 or height < 1000:
            scale = 2
            resized = cv2.resize(
                gray,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )
            images_to_try.append(resized)

        # 4. Adaptive threshold
        threshold = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            5
        )
        images_to_try.append(threshold)

        # 5. Otsu threshold
        _, otsu = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        images_to_try.append(otsu)

        # Try decoding with every version
        for image in images_to_try:

            # Normal QR detection
            data, points, _ = detector.detectAndDecode(image)

            if data:
                return data.strip()

            # Try multiple QR codes as well
            try:
                result = detector.detectAndDecodeMulti(image)

                if result[0]:
                    decoded_info = result[1]

                    for text in decoded_info:
                        if text:
                            return text.strip()

            except Exception:
                pass

        return None

    except Exception as e:
        print(f"QR decode error: {e}")
        return None
