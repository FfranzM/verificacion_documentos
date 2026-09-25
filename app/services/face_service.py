import cv2
import numpy as np

from insightface.app import FaceAnalysis


class FaceService:
    def __init__(self):
        self._app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
        )

        self._app.prepare(
            ctx_id=-1,
            det_size=(640, 640),
        )

    def _decode_image(self, content: bytes):
        image_array = np.frombuffer(content, dtype=np.uint8)

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR,
        )

        if image is None:
            raise ValueError("No fue posible leer la imagen.")

        return image

    def _get_faces(self, content: bytes):
        image = self._decode_image(content)

        return self._app.get(image)

    def compare(
        self,
        document_content: bytes,
        selfie_content: bytes,
    ) -> dict:
        document_faces = self._get_faces(document_content)
        selfie_faces = self._get_faces(selfie_content)

        if len(document_faces) == 0:
            return {
                "status": "document_face_not_detected",
                "matches": False,
                "similarity": 0.0,
            }

        if len(selfie_faces) == 0:
            return {
                "status": "selfie_face_not_detected",
                "matches": False,
                "similarity": 0.0,
            }

        if len(selfie_faces) > 1:
            return {
                "status": "multiple_faces_in_selfie",
                "matches": False,
                "similarity": 0.0,
            }

        # En una identificación esperamos utilizar
        # el rostro más grande detectado.
        document_face = max(
            document_faces,
            key=lambda face: self._face_area(face.bbox),
        )

        selfie_face = selfie_faces[0]

        document_embedding = document_face.normed_embedding
        selfie_embedding = selfie_face.normed_embedding

        similarity = float(
            np.dot(
                document_embedding,
                selfie_embedding,
            )
        )

        similarity = max(-1.0, min(similarity, 1.0))

        if similarity >= 0.50:
            status = "high"
            matches = True

        elif similarity >= 0.35:
            status = "review"
            matches = False

        else:
            status = "low"
            matches = False

        return {
            "status": status,
            "matches": matches,
            "similarity": round(similarity, 4),
        }

    def _face_area(self, bbox) -> float:
        x1, y1, x2, y2 = bbox

        return float(
            max(0, x2 - x1)
            * max(0, y2 - y1)
        )


face_service = FaceService()