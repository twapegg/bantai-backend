from openai import OpenAI
from app.config import settings

class ImageModerationService:
    """Service for moderating images using OpenAI's omni-moderation-latest model."""
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.openai_api_key
        self.client = OpenAI(api_key=self.api_key)

    async def moderate_image_url(self, image_url: str) -> dict:
        try:
            response = self.client.moderations.create(
                model="omni-moderation-latest",
                input=[
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            )
            return response.model_dump()
        except Exception as e:
            return {"error": str(e)}
