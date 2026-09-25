import re
import unicodedata

from rapidfuzz import fuzz


class NameMatcher:
    def _normalize(self, text: str) -> str:
        text = text.upper().strip()

        text = "".join(
            char
            for char in unicodedata.normalize("NFD", text)
            if unicodedata.category(char) != "Mn"
        )

        text = re.sub(r"[^A-Z\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def compare(
        self,
        expected_name: str,
        document_name: str | None,
    ) -> dict:
        if not document_name:
            return {
                "status": "unknown",
                "matches": False,
                "confidence": 0.0,
            }

        expected_words = self._normalize(expected_name).split()
        document_words = self._normalize(document_name).split()

        if not expected_words or not document_words:
            return {
                "status": "unknown",
                "matches": False,
                "confidence": 0.0,
            }

        matched = 0

        remaining_document_words = document_words.copy()

        for expected_word in expected_words:
            best_score = 0
            best_index = None

            for index, document_word in enumerate(remaining_document_words):
                score = fuzz.ratio(expected_word, document_word)

                if score > best_score:
                    best_score = score
                    best_index = index

            if best_score >= 85 and best_index is not None:
                matched += 1
                remaining_document_words.pop(best_index)

        confidence = matched / len(expected_words)

        if confidence >= 0.90:
            status = "high"
        elif confidence >= 0.60:
            status = "partial"
        else:
            status = "low"

        return {
            "status": status,
            "matches": status == "high",
            "confidence": round(confidence, 2),
        }


name_matcher = NameMatcher()