import json
import re
import urllib.error
import urllib.request

from flask import current_app


class TranslationService:
    SUPPORTED_LANGUAGES = {"en", "hi", "kn"}

    @staticmethod
    def _build_prompt(text: str, language: str):
        language_map = {"hi": "Hindi", "kn": "Kannada"}
        target = language_map.get(language, language)
        return (
            "Translate the following text from English to "
            f"{target}. Preserve punctuation, spacing, and line breaks. "
            "Return only the translated text. Do not include any explanation, notes, "
            "analysis, XML tags, or <think> blocks.\n"
            f"Text: {text}"
        )

    @staticmethod
    def _sanitize_translation_output(text: str) -> str:
        if not text:
            return ""

        cleaned = str(text)

        # Remove explicit reasoning blocks if model emits them.
        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)

        # Remove common assistant labels.
        cleaned = re.sub(
            r"^\s*(translation|translated text|output)\s*[:\-]\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = cleaned.strip()

        # Remove wrapping quotes added by some models.
        if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {'"', "'"}:
            cleaned = cleaned[1:-1].strip()

        return cleaned

    @staticmethod
    def _extract_completion_text(body):
        try:
            return body["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, AttributeError):
            return None

    @staticmethod
    def _translate_via_sarvam(text: str, target_language: str):
        api_key = current_app.config.get("SARVAM_API_KEY", "")
        if not api_key:
            return None

        payload = {
            "model": current_app.config.get("SARVAM_MODEL", "sarvam-m"),
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a strict translation assistant. "
                        "Return only translated text and never include reasoning or markup."
                    ),
                },
                {
                    "role": "user",
                    "content": TranslationService._build_prompt(text, target_language),
                },
            ],
            "temperature": 0.2,
        }

        request = urllib.request.Request(
            "https://api.sarvam.ai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                body = json.loads(response.read().decode("utf-8"))
                raw = TranslationService._extract_completion_text(body)
                return TranslationService._sanitize_translation_output(raw)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return None

    @staticmethod
    def translate_text(text: str, target_language: str) -> str:
        if not text:
            return ""

        if (target_language or "").lower() == "en":
            return text

        normalized_language = (target_language or "").strip().lower()
        if normalized_language not in TranslationService.SUPPORTED_LANGUAGES:
            normalized_language = "en"

        if normalized_language == "en":
            return text

        sarvam_text = TranslationService._translate_via_sarvam(text, normalized_language)
        if sarvam_text:
            return sarvam_text

        api_key = current_app.config.get("OPENAI_API_KEY", "")
        if not api_key:
            return f"[{normalized_language}] {text}"

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a translation assistant."},
                {"role": "user", "content": TranslationService._build_prompt(text, normalized_language)},
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
                return TranslationService._sanitize_translation_output(
                    body["choices"][0]["message"]["content"]
                )
        except (urllib.error.URLError, KeyError, IndexError, TimeoutError, json.JSONDecodeError):
            return f"[{normalized_language}] {text}"

    @staticmethod
    def translate_texts(texts, target_language: str):
        cache = {}
        translated = {}
        for text in texts:
            key = str(text or "")
            if key in cache:
                translated[key] = cache[key]
                continue
            print(f"Translating: {key}", flush=True)

            value = TranslationService.translate_text(key, target_language)
            cache[key] = value
            translated[key] = value

        return translated

    @staticmethod
    def translate_mapping(mapping, target_language: str):
        keys = list(mapping.keys())
        texts = [mapping[key] for key in keys]
        translated = TranslationService.translate_texts(texts, target_language)
        return {key: translated.get(mapping[key], mapping[key]) for key in keys}


def translate_text(text: str, target_language: str) -> str:
    return TranslationService.translate_text(text, target_language)
