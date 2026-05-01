from io import BytesIO
import unittest

from PIL import Image

from app.module.convert_tools.image_to_pdf.services import UploadedImage, create_pdf_from_images


def make_image_bytes(fmt: str = "PNG", color=(255, 0, 0, 255)) -> bytes:
    mode = "RGBA" if len(color) == 4 else "RGB"
    image = Image.new(mode, (50, 50), color=color)
    buffer = BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


class ConvertToolsServiceTests(unittest.TestCase):
    def test_create_pdf_from_images_returns_pdf(self) -> None:
        images = [
            UploadedImage(filename="one.png", content_type="image/png", data=make_image_bytes("PNG")),
            UploadedImage(filename="two.jpg", content_type="image/jpeg", data=make_image_bytes("JPEG", color=(0, 255, 0))),
        ]

        pdf = create_pdf_from_images(images)

        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 100)

    def test_create_pdf_from_images_rejects_invalid_type(self) -> None:
        images = [UploadedImage(filename="bad.txt", content_type="text/plain", data=b"hello")]

        with self.assertRaises(ValueError):
            create_pdf_from_images(images)


if __name__ == "__main__":
    unittest.main()
