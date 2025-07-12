
import requests

class OCRService:
    """Service for handling OCR operations using the ocr.space API."""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.ocr.space/parse/image"

    async def ocr_image_url(self, image_url: str) -> dict:
        """Send an image URL to the OCR API and return the parsed text or error."""
        response = requests.post(
            self.endpoint,
            data={"apikey": self.api_key, "url": image_url}
        )
        result = response.json()
        if 'ParsedResults' in result:
            return {"text": result['ParsedResults'][0]['ParsedText']}
        return {"error": result}
