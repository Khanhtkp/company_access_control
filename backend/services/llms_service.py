import google.generativeai as genai
from ..interfaces.llms_api import ILLMService
class GeminiLLMService(ILLMService):
    def __init__(self, api_key: str):
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        genai.configure(api_key=api_key)

    def generate_report(self, prompt: str) -> str:
        response = self.model.generate_content(
            prompt
        )
        return response.text