"""Server-side image validation based on actual file content (not filename or Content-Type)."""
import io
from PIL import Image, UnidentifiedImageError
MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 25_000_000
ALLOWED = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
class ImageError(ValueError): pass
def validate_image(data: bytes) -> str:
    """Return the safe file extension for valid image bytes, else raise ImageError."""
    if not data: raise ImageError("The uploaded file is empty.")
    if len(data) > MAX_BYTES: raise ImageError("Image must be 5 MB or smaller.")
    try:
        with Image.open(io.BytesIO(data)) as im:
            fmt, (w, h) = im.format, im.size
            if fmt not in ALLOWED: raise ImageError("Only JPEG, PNG and WebP images are allowed.")
            if w * h > MAX_PIXELS: raise ImageError("Image dimensions are too large (max 25 megapixels).")
            im.load()  # fully decode: catches truncated or corrupt files
    except ImageError: raise
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError, ValueError):
        raise ImageError("The file is not a valid image.")
    return ALLOWED[fmt]