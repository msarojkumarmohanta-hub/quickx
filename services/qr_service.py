from __future__ import annotations

import io

import qrcode
from PIL import Image

try:
    from pyzbar.pyzbar import decode
except Exception:
    decode = None


def generate_qr_code(data: str, file_path: str):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)
    return file_path


def decode_qr_from_image(uploaded_file):
    if decode is None:
        return None
    try:
        image = Image.open(uploaded_file)
        decoded = decode(image)
        if decoded:
            return decoded[0].data.decode("utf-8")
    except Exception:
        return None
    return None


def build_qr_text(campus, building, floor, room, area):
    return f"{campus}|{building}|{floor}|{room}|{area}"
