import base64
from io import BytesIO


def create_placeholder_base64(width: int = 1, height: int = 1, color: tuple = (0, 0, 0)) -> str:

    try:
        from PIL import Image
        img = Image.new('RGB', (width, height), color)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    except ImportError:
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

PLACEHOLDER_BASE64 = create_placeholder_base64(1, 1, (0, 0, 0))

def get_placeholder_image() -> str:
    return PLACEHOLDER_BASE64
