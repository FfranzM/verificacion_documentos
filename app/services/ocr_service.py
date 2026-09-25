from paddleocr import PaddleOCR


class OCRService:
    def __init__(self):
        self._ocr = PaddleOCR(
            lang="es",
            use_doc_orientation_classify=True,
            use_doc_unwarping=True,
            use_textline_orientation=True,
        )

    def analyze(self, file_path: str) -> list[dict]:
        results = self._ocr.predict(file_path)

        extracted_lines = []

        for result in results:
            data = result.json

            if "res" not in data:
                continue

            res = data["res"]

            texts = res.get("rec_texts", [])
            scores = res.get("rec_scores", [])

            for text, score in zip(texts, scores):
                extracted_lines.append(
                    {
                        "text": text,
                        "confidence": round(float(score), 4),
                    }
                )

        return extracted_lines


ocr_service = OCRService()