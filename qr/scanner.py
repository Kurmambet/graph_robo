import json
from typing import Optional

import cv2


def scan_qr_once(timeout_seconds: int = 15) -> Optional[dict]:
    """
    Открывает веб-камеру и ждёт QR-код не дольше timeout_seconds.
    Возвращает распарсенный словарь или None если не удалось.

    Ожидаемый формат QR:
        {"forward": true, "back": false, "left": true, "right": false}
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[QR] Камера недоступна")
        return None

    detector = cv2.QRCodeDetector()

    import time

    deadline = time.time() + timeout_seconds

    result = None
    while time.time() < deadline:
        ret, frame = cap.read()
        if not ret:
            continue

        data, _, _ = detector.detectAndDecode(frame)

        cv2.imshow("QR Scanner - ESC for exit", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break

        if data:
            try:
                result = json.loads(data)
                print(f"[QR] Считано: {result}")
                break
            except json.JSONDecodeError:
                print(f"[QR] Не JSON: {data!r}")

    cap.release()
    cv2.destroyAllWindows()
    return result
