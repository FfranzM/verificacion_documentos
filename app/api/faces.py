from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.services.face_service import face_service
from app.core.security import verify_api_key

router = APIRouter(
    prefix="/api/v1/faces",
    tags=["Faces"],
)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/compare", dependencies=[Depends(verify_api_key)])
async def compare_faces(
    document: UploadFile = File(...),
    selfie: UploadFile = File(...),
):
    if document.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="El documento debe ser JPG, PNG o WEBP.",
        )

    if selfie.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="La selfie debe ser JPG, PNG o WEBP.",
        )

    document_content = await document.read()
    selfie_content = await selfie.read()

    if not document_content:
        raise HTTPException(
            status_code=400,
            detail="La imagen del documento está vacía.",
        )

    if not selfie_content:
        raise HTTPException(
            status_code=400,
            detail="La selfie está vacía.",
        )

    if len(document_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="La imagen del documento supera el límite de 10 MB.",
        )

    if len(selfie_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="La selfie supera el límite de 10 MB.",
        )

    try:
        result = face_service.compare(
            document_content=document_content,
            selfie_content=selfie_content,
        )

        return {
            "success": True,
            "face_match": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible comparar los rostros: {str(exc)}",
        ) from exc