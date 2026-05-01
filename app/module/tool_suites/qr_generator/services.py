import qrcode
import logging
import io
from typing import Optional
from PIL import Image, ImageDraw
from pyzbar.pyzbar import decode

logger = logging.getLogger(__name__)

ERROR_MAPPING = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


def generate_basic_qr(data: str, size: int = 512) -> io.BytesIO:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size), Image.Resampling.LANCZOS)

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr


def generate_advanced_qr(
    data: str,
    error_correction: str,
    logo_shape: str,
    logo_size_percent: int,
    white_margin: int,
    logo_bytes: Optional[bytes] = None,
) -> io.BytesIO:

    # 3. Lógica de Generación Estética
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_MAPPING.get(
            error_correction[:1].upper(), qrcode.constants.ERROR_CORRECT_H
        ),
        box_size=15,
        border=white_margin,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Crear imagen base
    img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_w, qr_h = img_qr.size

    if logo_bytes:
        # Abrir logo y asegurar canal Alpha para transparencias
        logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")

        # Cálculo de tamaño dinámico estético
        ratio = logo_size_percent / 100
        logo_size = int(qr_w * ratio)
        padding = max(8, int(logo_size * 0.08))

        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # Crear lienzo para el logo con su fondo blanco/recorte
        pos_x = (qr_w - logo_size) // 2
        pos_y = (qr_h - logo_size) // 2

        # Dibujar el área blanca protectora detrás del logo
        draw = ImageDraw.Draw(img_qr)

        if logo_shape == "circular":
            # Fondo blanco circular
            offset = padding
            draw.ellipse(
                [
                    pos_x - offset,
                    pos_y - offset,
                    pos_x + logo_size + offset,
                    pos_y + logo_size + offset,
                ],
                fill="white",
            )

            # Recortar logo circularmente
            mask = Image.new("L", (logo_size, logo_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, logo_size, logo_size), fill=255)
            img_qr.paste(logo, (pos_x, pos_y), mask)

        else:  # Redondeada
            radius = int(logo_size * 0.15)
            offset = padding // 2
            # Fondo blanco redondeado
            draw.rounded_rectangle(
                [
                    pos_x - offset,
                    pos_y - offset,
                    pos_x + logo_size + offset,
                    pos_y + logo_size + offset,
                ],
                radius=radius,
                fill="white",
            )

            # Recortar logo redondeado
            mask = Image.new("L", (logo_size, logo_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                [0, 0, logo_size, logo_size], radius=radius, fill=255
            )
            img_qr.paste(logo, (pos_x, pos_y), mask)

    img_byte_arr = io.BytesIO()
    img_qr.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr


def decode_qr(image_bytes: bytes) -> Optional[str]:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        decoded_objects = decode(img)
        if decoded_objects:
            return decoded_objects[0].data.decode("utf-8")
        return None
    except Exception as e:
        logger.error(f"Error decoding QR: {e}", exc_info=True)
        return None
