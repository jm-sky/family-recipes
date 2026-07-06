"""Recipe image upload handling."""

import logging
import uuid
from io import BytesIO

from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.core.config import settings
from app.core.storage.exceptions import CorruptedImageError
from app.core.storage.factory import get_storage_adapter
from app.core.storage.image_processor import ImageProcessor
from app.modules.recipes.db_models import RecipeDB
from app.modules.recipes.repository import RecipeRepository

logger = logging.getLogger(__name__)

MIME_TO_EXTENSION = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


class RecipeImageService:
    """Upload and remove recipe cover images."""

    def __init__(self, repository: RecipeRepository):
        self.repository = repository
        self.storage = get_storage_adapter()
        self.processor = ImageProcessor(
            max_width=settings.storage.max_width,
            max_height=settings.storage.max_height,
            jpeg_quality=settings.storage.jpeg_quality,
            convert_to_webp=settings.storage.convert_to_webp,
        )
        self.max_file_size = settings.storage.max_file_size
        self.allowed_mime_types = set(settings.storage.allowed_mime_types)

    async def upload(self, recipe: RecipeDB, file: UploadFile) -> str:
        """Process and store a recipe image; returns public URL."""
        content = await file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
        if len(content) > self.max_file_size:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")

        mime_type = file.content_type or "application/octet-stream"
        if mime_type not in self.allowed_mime_types:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type: {mime_type}")

        try:
            processed_bytes, processed_mime, _, _ = await self.processor.process_image(content, mime_type)
        except CorruptedImageError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        extension = MIME_TO_EXTENSION.get(processed_mime, ".jpg")
        destination = f"recipes/{recipe.family_id}/{recipe.id}/{uuid.uuid4().hex}{extension}"

        if recipe.image_path:
            await self.storage.delete(recipe.image_path)

        stored_path = await self.storage.upload(processed_bytes, destination, processed_mime)
        await self.repository.set_image_path(recipe, stored_path)
        return await self.storage.get_url(stored_path)

    async def resolve_url(self, image_path: str | None) -> str | None:
        if not image_path:
            return None
        return await self.storage.get_url(image_path)

    @staticmethod
    def sniff_mime(content: bytes) -> str:
        """Best-effort MIME detection when client omits content type."""
        try:
            with Image.open(BytesIO(content)) as img:
                fmt = (img.format or "JPEG").upper()
        except OSError:
            return "application/octet-stream"
        mapping = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp", "GIF": "image/gif"}
        return mapping.get(fmt, "image/jpeg")
