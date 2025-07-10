"""
Minimized Image Classification Service
"""
import asyncio
import requests
import base64
from typing import Dict, Any
import logging
from io import BytesIO

from PIL import Image, ImageFilter
from app.config import settings

logger = logging.getLogger(__name__)


class ImageClassifier:
    def __init__(self):
        self.api_user = settings.sightengine_api_user
        self.api_secret = settings.sightengine_api_secret
        self.base_url = "https://api.sightengine.com/1.0/check.json"
        self.threshold = settings.image_confidence_threshold
    
    async def classify_image(self, image_data: bytes, blur_unsafe: bool = True) -> Dict[str, Any]:
        """Classify and optionally blur harmful images."""
        try:
            result = await self._classify_with_sightengine(image_data)
            if blur_unsafe and result.get("label") == "unsafe":
                result["blurred_image"] = self._blur_image(image_data)
            return result
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "reason": str(e)}
    
    async def classify_image_url(self, image_url: str, blur_unsafe: bool = True) -> Dict[str, Any]:
        """Classify image from URL."""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: requests.get(image_url, timeout=10))
            return await self.classify_image(response.content, blur_unsafe)
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "reason": str(e)}
    
    async def classify_data_url(self, data_url: str, blur_unsafe: bool = True) -> Dict[str, Any]:
        """Classify image from data URL."""
        try:
            base64_data = data_url.split(',', 1)[1]
            image_data = base64.b64decode(base64_data)
            return await self.classify_image(image_data, blur_unsafe)
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "reason": str(e)}
    
    async def _classify_with_sightengine(self, image_data: bytes) -> Dict[str, Any]:
        """Classify using SightEngine API."""
        try:
            data = {'api_user': self.api_user, 'api_secret': self.api_secret, 
                   'models': 'nudity,weapon,alcohol,violence,gore,gambling,medical'}
            files = {'media': image_data}
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: requests.post(self.base_url, files=files, data=data))
            
            return self._parse_response(response.json())
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "reason": str(e)}
    
    def _parse_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse SightEngine response."""
        try:
            issues = []
            max_confidence = 0.0
            
            for detection_type, fields in [('nudity', ['raw', 'partial']), ('weapon', ['classes']), 
                                         ('alcohol', ['prob']), ('violence', ['prob']), ('gore', ['prob']), 
                                         ('gambling', ['prob']), ('medical', ['prob'])]:
                if detection_type in result:
                    confidence = self._extract_confidence(result[detection_type], fields)
                    if confidence > self.threshold:
                        max_confidence = max(max_confidence, confidence)
                        issues.append(f"{detection_type} detected")
            
            return {"label": "unsafe", "confidence": round(max_confidence, 2), "reason": "; ".join(issues)} if issues else \
                   {"label": "safe", "confidence": 0.95, "reason": "No inappropriate content detected"}
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "reason": str(e)}
    
    def _extract_confidence(self, detection_data: Dict, fields: list) -> float:
        """Extract confidence score."""
        max_conf = 0.0
        for field in fields:
            if field == 'classes' and 'classes' in detection_data:
                max_conf = max(max_conf, max(detection_data['classes'].values()))
            elif field in detection_data:
                max_conf = max(max_conf, detection_data[field])
        return max_conf
    
    def _blur_image(self, image_data: bytes) -> str:
        """Blur image and return as base64."""
        try:
            image = Image.open(BytesIO(image_data))
            blurred = image.filter(ImageFilter.GaussianBlur(radius=15))
            buffer = BytesIO()
            blurred.save(buffer, format='JPEG', quality=85)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception:
            return ""
