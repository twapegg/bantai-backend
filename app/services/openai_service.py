import os
from openai import OpenAI

class OpenAIService:
    async def analyze_emotion(self, text: str, active_categories=None, category_scores=None) -> dict:
        """Analyze the emotional tone of the given text using OpenAI's chat model, with moderation context."""
        import json
        try:
            if active_categories is None:
                active_categories = []
            if category_scores is None:
                category_scores = {}
            prompt = (
                "You are an emotional tone analyzer for digital content moderation.\n\n"
                "A piece of content was flagged by an AI moderation model for containing potentially harmful material.\n\n"
                "Here are the flagged moderation categories:\n"
                f"- {', '.join(active_categories)}\n\n"
                "Category severity scores:\n"
                f"{json.dumps(category_scores, indent=2)}\n\n"
                "Your job is to assess:\n\n"
                "1. The emotional and psychological theme the content may carry (e.g. aggression, fear).\n"
                "2. Possible risks or mental health concerns associated with the exposure to this content to the child.\n"
                "3. Actionable steps the parent should take to ensure the child's emotional and digital well-being.\n"
                "Avoid assuming the author is the child — the content may have been read or seen by them.\n\n"
                "Return a paragraph with your emotional/psychological interpretation in a way that the parent using can understand.\n\n"
                f"Content to analyze:\n{text}"
            )
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt}
                ]
            )
            return {"emotion_analysis": response.choices[0].message.content}
        except Exception as e:
            return {"error": str(e)}
    """Service for analyzing text using OpenAI's moderation API."""
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    async def analyze_text(self, text: str) -> dict:
        # Uses the omni-moderation-latest model for text moderation/analysis
        try:
            response = self.client.moderations.create(
                model="omni-moderation-latest",
                input=text
            )
            data = response.model_dump()
            flagged = data.get("flagged", False)
            return {"flagged": flagged, "analysis": data}
        except Exception as e:
            return {"error": str(e)}
