import unicodedata


class DocumentClassifier:
    DOCUMENTS = {
        "birth_certificate": {
            "threshold": 0.60,
            "keywords": {
                "ACTA DE NACIMIENTO": 0.50,
                "DATOS DE LA PERSONA REGISTRADA": 0.20,
                "NUMERO DE ACTA": 0.10,
                "OFICIALIA": 0.10,
                "LIBRO": 0.05,
                "NUMERO DE CERTIFICADO DE NACIMIENTO": 0.20,
            },
            "negative_keywords": {},
        },
        "ine": {
            "threshold": 0.60,
            "keywords": {
                "INSTITUTO NACIONAL ELECTORAL": 0.35,
                "CREDENCIAL PARA VOTAR": 0.30,
                "CLAVE DE ELECTOR": 0.15,
                "CURP": 0.10,
                "SECCION": 0.05,
                "VIGENCIA": 0.05,
            },
        },
        "license": {
            "threshold": 0.50,
            "keywords": {
                "LICENCIA DE CONDUCIR": 0.40,
                "LICENCIA PARA CONDUCIR": 0.40,
                "TIPO DE LICENCIA": 0.15,
                "NUMERO DE LICENCIA": 0.15,
                "EXPEDICION": 0.10,
                "VIGENCIA": 0.10,
            },
        },
        "curp": {
            "threshold": 0.60,

            "keywords": {
                "CONSTANCIA DE LA CLAVE UNICA DE REGISTRO DE POBLACION": 0.45,
                "CURP CERTIFICADA": 0.30,
                "RENAPO": 0.20,
                "GOBERNACION": 0.10,
                "ENTIDAD DE REGISTRO": 0.05,
            },

            "exclude_if_contains": [
                "ACTA DE NACIMIENTO",
                "NUMERO DE CERTIFICADO DE NACIMIENTO",
            ],
        },
        "insurance_policy": {
            "threshold": 0.50,
            "keywords": {
                "POLIZA DE SEGURO": 0.35,
                "NUMERO DE POLIZA": 0.20,
                "ASEGURADO": 0.15,
                "COBERTURA": 0.10,
                "VIGENCIA": 0.10,
                "PRIMA": 0.05,
                "SUMA ASEGURADA": 0.05,
            },
        },
    }

    def _normalize(self, text: str) -> str:
        text = text.upper()

        text = "".join(
            char
            for char in unicodedata.normalize("NFD", text)
            if unicodedata.category(char) != "Mn"
        )

        return text

    def classify(self, text: str) -> dict:
        normalized_text = self._normalize(text)

        results = []

        for document_type, config in self.DOCUMENTS.items():

            excluded = any(
                phrase in normalized_text
                for phrase in config.get("exclude_if_contains", [])
            )

            if excluded:
                results.append(
                    {
                        "document_type": document_type,
                        "score": 0.0,
                        "threshold": config["threshold"],
                    }
                )
                continue

            score = 0.0

            for keyword, weight in config["keywords"].items():
                if keyword in normalized_text:
                    score += weight

            for keyword, weight in config.get(
                "negative_keywords",
                {},
            ).items():
                if keyword in normalized_text:
                    score -= weight

            score = max(0.0, min(score, 1.0))

            results.append(
                {
                    "document_type": document_type,
                    "score": score,
                    "threshold": config["threshold"],
                }
            )

        best = max(
            results,
            key=lambda item: item["score"],
        )

        if best["score"] >= best["threshold"]:
            return {
                "document_type": best["document_type"],
                "recognized": True,
                "confidence": round(best["score"], 2),
                "message": "Documento reconocido.",
            }

        return {
            "document_type": "unknown",
            "recognized": False,
            "confidence": round(best["score"], 2),
            "message": "No se pudo identificar el tipo de documento.",
        }


document_classifier = DocumentClassifier()