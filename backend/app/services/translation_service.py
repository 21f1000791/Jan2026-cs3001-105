import json
import re
import urllib.error
import urllib.request

from flask import current_app


class TranslationService:
    SUPPORTED_LANGUAGES = {"en", "hi", "kn"}
    CATEGORY_TRANSLATIONS = {
        "hi": {
            "Maintenance": "रखरखाव",
            "Construction": "निर्माण",
            "Electrical": "विद्युत",
            "Sanitation": "स्वच्छता",
            "Landscaping": "भू-दृश्य",
        },
        "kn": {
            "Maintenance": "ನಿರ್ವಹಣೆ",
            "Construction": "ನಿರ್ಮಾಣ",
            "Electrical": "ವಿದ್ಯುತ್",
            "Sanitation": "ಸ್ವಚ್ಛತೆ",
            "Landscaping": "ಭೂ ಅಲಂಕಾರ",
        },
    }

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

        # Remove unclosed or malformed leading think tags.
        cleaned = re.sub(r"^\s*<think>\s*", "", cleaned, flags=re.IGNORECASE)

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
    def _is_reasoning_leak(text: str) -> bool:
        value = (text or "").strip()
        if not value:
            return False

        lowered = value.lower()
        leak_markers = [
            "<think>",
            "let's tackle",
            "first, i need to",
            "user wants",
            "translation task",
            "double-check",
            "make sure",
            "putting it together",
        ]
        return any(marker in lowered for marker in leak_markers)

    @staticmethod
    def _extract_last_non_empty_line(text: str) -> str:
        lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
        return lines[-1] if lines else ""

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
                cleaned = TranslationService._sanitize_translation_output(raw)

                # If reasoning leaked, attempt to salvage the final line only.
                if TranslationService._is_reasoning_leak(cleaned):
                    cleaned = TranslationService._extract_last_non_empty_line(cleaned)

                if TranslationService._is_reasoning_leak(cleaned):
                    return None

                return cleaned
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
            return text

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
                cleaned = TranslationService._sanitize_translation_output(
                    body["choices"][0]["message"]["content"]
                )
                if TranslationService._is_reasoning_leak(cleaned):
                    cleaned = TranslationService._extract_last_non_empty_line(cleaned)
                if TranslationService._is_reasoning_leak(cleaned):
                    return text
                return cleaned
        except (urllib.error.URLError, KeyError, IndexError, TimeoutError, json.JSONDecodeError):
            return text

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

    @staticmethod
    def localize_category(category: str, target_language: str) -> str:
        value = (category or "").strip()
        lang = (target_language or "en").strip().lower()
        if not value or lang == "en":
            return value

        mapped = TranslationService.CATEGORY_TRANSLATIONS.get(lang, {}).get(value)
        if mapped:
            return mapped

        translated = TranslationService.translate_text(value, lang)
        placeholder = f"[{lang}]"
        if translated and not translated.strip().startswith(placeholder):
            return translated
        return value


def translate_text(text: str, target_language: str) -> str:
    return TranslationService.translate_text(text, target_language)
