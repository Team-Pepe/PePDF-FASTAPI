from io import BytesIO
import unittest

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


def make_image_file(fmt: str = "PNG") -> bytes:
    image = Image.new("RGB", (32, 32), color=(120, 20, 200))
    stream = BytesIO()
    image.save(stream, format=fmt)
    return stream.getvalue()


class ConvertToolsRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_image_to_pdf_success(self) -> None:
        image1 = make_image_file("PNG")
        image2 = make_image_file("JPEG")

        response = self.client.post(
            "/convert-tools/image-to-pdf",
            files=[
                ("files", ("one.png", image1, "image/png")),
                ("files", ("two.jpg", image2, "image/jpeg")),
            ],
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_image_to_pdf_rejects_invalid_file(self) -> None:
        response = self.client.post(
            "/convert-tools/image-to-pdf",
            files=[("files", ("bad.txt", b"abc", "text/plain"))],
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
