import os
import tempfile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.services.document_classifier import document_classifier
from app.services.document_field_extractor import document_field_extractor
from app.services.name_matcher import name_matcher
from app.services.ocr_service import ocr_service
from app.core.security import verify_api_key


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/analyze", dependencies=[Depends(verify_api_key)])
async def analyze_document(
    file: UploadFile = File(...),
    name: str = Form(...),
    debug: bool = Form(False),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Tipo de archivo no permitido. Usa JPG, PNG, WEBP o PDF.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío.",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="El archivo supera el límite de 10 MB.",
        )

    suffix = os.path.splitext(file.filename or "")[1]

    if not suffix:
        suffix = (
            ".pdf"
            if file.content_type == "application/pdf"
            else ".jpg"
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        lines = ocr_service.analyze(temp_path)

        full_text = "\n".join(
            line["text"]
            for line in lines
        )

        analysis = document_classifier.classify(full_text)


        fields = document_field_extractor.extract(
            document_type=analysis["document_type"],
            lines=lines,
        )

        name_analysis = name_matcher.compare(
            expected_name=name,
            document_name=fields["name"],
        )

        # Construir respuesta normal
        response = {
            "success": True,
            "analysis": {
                "document_type": analysis["document_type"],
                "recognized": analysis["recognized"],
                "document_confidence": analysis["confidence"],
                "name_match": {
                    "status": name_analysis["status"],
                    "matches": name_analysis["matches"],
                    "confidence": name_analysis["confidence"],
                },
            },
        }

        #Información adicional solo para desarrollo
        if debug:
            response["debug"] = {
                "extracted_name": fields["name"],
                "ocr_text": full_text,
            }

        return response

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible analizar el documento: {str(exc)}",
        ) from exc

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)