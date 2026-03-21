import json
import urllib.error
import urllib.request

from flask import current_app


class TranslationService:
    @staticmethod
    def _build_prompt(text: str, language: str):
        language_map = {"hi": "Hindi", "kn": "Kannada"}
        target = language_map.get(language, language)
        return (
            "Translate the following operational task text to "
            f"{target}. Return only translated text. Text: {text}"
        )

    @staticmethod
    def translate_text(text: str, target_language: str) -> str:
        if not text:
            return ""

        api_key = current_app.config.get("OPENAI_API_KEY", "")
        if not api_key:
            return f"[{target_language}] {text}"

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a translation assistant."},
                {"role": "user", "content": TranslationService._build_prompt(text, target_language)},
            ],
            "temperature": 0.2,
        }

        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=12) as response:
                body = json.loads(response.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"].strip()
        except (urllib.error.URLError, KeyError, IndexError, TimeoutError, json.JSONDecodeError):
            return f"[{target_language}] {text}"


def translate_text(text: str, target_language: str) -> str:
    return TranslationService.translate_text(text, target_language)
