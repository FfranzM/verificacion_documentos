class DocumentFieldExtractor:
    def extract(
        self,
        document_type: str,
        lines: list[dict],
    ) -> dict:
        texts = [
            line["text"].strip()
            for line in lines
            if line.get("text", "").strip()
        ]
        if document_type == "birth_certificate":
            return self._extract_birth_certificate(texts)

        if document_type == "ine":
            return self._extract_ine(texts)

        if document_type == "curp":
            return self._extract_curp(texts)

        if document_type == "license":
            return self._extract_license(texts)

        if document_type == "insurance_policy":
            return self._extract_insurance_policy(texts)

        return {"name": None}

    def _extract_birth_certificate(self,lines: list[str],) -> dict:
        start_index = None
        end_index = None

        for index, line in enumerate(lines):
            normalized = line.upper().strip()

            if normalized == "DATOS DE LA PERSONA REGISTRADA":
                start_index = index + 1
                break

        if start_index is None:
            return {"name": None}

        for index in range(start_index, len(lines)):
            normalized = lines[index].upper().strip()

            if normalized.startswith("NOMBRE(S)"):
                end_index = index
                break

        if end_index is None:
            return {"name": None}

        name_parts = [
            line.strip()
            for line in lines[start_index:end_index]
            if line.strip()
        ]

        if not name_parts:
            return {"name": None}

        return {
            "name": " ".join(name_parts),
        }

    def _extract_ine(self, lines: list[str]) -> dict:
        name = self._extract_between(
            lines,
            start_labels=["NOMBRE"],
            end_labels=["DOMICILIO"],
        )

        return {"name": name}

    def _extract_curp(self, lines: list[str]) -> dict:
        name = self._extract_after_label(
            lines,
            labels=[
                "NOMBRE",
                "NOMBRE(S)",
            ],
        )

        return {"name": name}

    def _extract_license(self, lines: list[str]) -> dict:
        name = self._extract_after_label(
            lines,
            labels=[
                "NOMBRE",
                "NOMBRE COMPLETO",
                "NOMBRE DEL CONDUCTOR",
            ],
        )

        return {"name": name}

    def _extract_insurance_policy(self, lines: list[str]) -> dict:
        name = self._extract_after_label(
            lines,
            labels=[
                "ASEGURADO",
                "NOMBRE DEL ASEGURADO",
                "CONTRATANTE",
            ],
        )

        return {"name": name}

    def _extract_between(
        self,
        lines: list[str],
        start_labels: list[str],
        end_labels: list[str],
    ) -> str | None:
        start_index = None

        for index, line in enumerate(lines):
            normalized = line.upper().strip()

            if normalized in start_labels:
                start_index = index + 1
                break

        if start_index is None:
            return None

        result = []

        for line in lines[start_index:]:
            normalized = line.upper().strip()

            if normalized in end_labels:
                break

            result.append(line)

        if not result:
            return None

        return " ".join(result)

    def _extract_after_label(
        self,
        lines: list[str],
        labels: list[str],
    ) -> str | None:
        for index, line in enumerate(lines):
            normalized = line.upper().strip()

            if normalized in labels:
                if index + 1 < len(lines):
                    return lines[index + 1].strip()

            for label in labels:
                if normalized.startswith(f"{label}:"):
                    value = line.split(":", 1)[1].strip()

                    if value:
                        return value

        return None


document_field_extractor = DocumentFieldExtractor()