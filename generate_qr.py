import itertools
import json
import os

import qrcode
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "qr_codes"
DIRECTIONS = ["forward", "back", "left", "right"]
LABELS = {
    "forward": "Вперёд",
    "back": "Назад",
    "left": "Влево",
    "right": "Вправо",
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

SHORT = {"forward": "F", "back": "B", "left": "L", "right": "R"}

# Все комбинации хотя бы с одним True
combos = []
for r in range(1, 5):
    for combo in itertools.combinations(DIRECTIONS, r):
        combos.append(combo)

for combo in combos:
    qr_data = {d: (d in combo) for d in DIRECTIONS}
    json_str = json.dumps(qr_data, separators=(",", ":"))

    # --- QR код ---
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(json_str)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    qr_w, qr_h = qr_img.size
    pad = 20
    label_h = 100  # высота области с подписями

    canvas_w = qr_w + pad * 2
    canvas_h = qr_h + pad * 2 + label_h
    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    canvas.paste(qr_img, (pad, pad))

    draw = ImageDraw.Draw(canvas)

    # --- Шрифты ---
    # Если нет системного шрифта, PIL возьмёт дефолтный
    try:
        font_title = ImageFont.truetype("arial.ttf", 18)
        font_body = ImageFont.truetype("arial.ttf", 14)
        font_json = ImageFont.truetype("cour.ttf", 11)  # моноширинный
    except OSError:
        try:
            # Linux путь
            font_title = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18
            )
            font_body = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14
            )
            font_json = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 11
            )
        except OSError:
            font_title = ImageFont.load_default()
            font_body = font_title
            font_json = font_title

    y = qr_h + pad * 2

    # --- Строка «Открыто: Вперёд  Влево» ---
    open_dirs = [LABELS[d] for d in DIRECTIONS if qr_data[d]]
    closed_dirs = [LABELS[d] for d in DIRECTIONS if not qr_data[d]]

    draw.text((pad, y), "Открыто:", fill="#000000", font=font_body)
    draw.text((pad + 80, y), "  ".join(open_dirs), fill="#1a7a1a", font=font_title)

    # --- Строка «Закрыто: Назад  Вправо» ---
    if closed_dirs:
        draw.text((pad, y + 28), "Закрыто:", fill="#000000", font=font_body)
        draw.text(
            (pad + 80, y + 28), "  ".join(closed_dirs), fill="#cc2222", font=font_body
        )

    # --- JSON мелко для проверки ---
    draw.text((pad, y + 62), json_str, fill="#999999", font=font_json)

    # --- Сохраняем ---
    name = "_".join(SHORT[d] for d in combo)
    canvas.save(os.path.join(OUTPUT_DIR, f"qr_{name}.png"))
    print(f"  {name}")

print(f"\nГотово: {len(combos)} QR-кодов в папке '{OUTPUT_DIR}/'")
