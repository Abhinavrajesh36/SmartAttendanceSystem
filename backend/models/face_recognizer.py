"""
Face Recognition & Detection — InsightFace buffalo_l
=====================================================
Single shared FaceAnalysis instance loads both detection + recognition.
InsightFace asserts detection must always be present in FaceAnalysis.
"""

import cv2
import numpy as np
from typing import List, Tuple

# Shared app instance — initialised once at module level on first use
_shared_app = None

def _get_app(device: str = "cpu"):
    global _shared_app
    if _shared_app is None:
        from insightface.app import FaceAnalysis
        ctx_id = 0 if device == "cuda" else -1
        _shared_app = FaceAnalysis(
            name="buffalo_l",
            allowed_modules=["detection", "recognition"]
        )
        _shared_app.prepare(ctx_id=ctx_id, det_size=(640, 640))
        print("InsightFace buffalo_l loaded (detection + recognition).")
    return _shared_app


class RetinaFaceDetector:
    def __init__(self, model_path=None, device="cpu", conf_threshold=0.35, **kwargs):
        self.conf_threshold = conf_threshold
        self._app = _get_app(device)
        print("RetinaFace detector ready.")

    def detect(self, frame: np.ndarray) -> List[Tuple[int,int,int,int]]:
        return [bbox for bbox, _ in self.detect_with_kps(frame)]

    def detect_with_kps(self, frame: np.ndarray):
        faces = self._app.get(frame)
        results = []
        for face in faces:
            if face.det_score < self.conf_threshold:
                continue
            x1, y1, x2, y2 = face.bbox.astype(int)
            kps = face.kps.astype(np.float32)
            results.append(((x1, y1, x2, y2), kps))
        results.sort(key=lambda r: (r[0][2]-r[0][0])*(r[0][3]-r[0][1]), reverse=True)
        return results


# Alias for any remaining imports
YOLOv9FaceDetector = RetinaFaceDetector


class ArcFaceRecognizer:
    def __init__(self, model_path=None, embedding_size=512, device="cpu"):
        app = _get_app(device)
        # Get recognition model directly — no separate FaceAnalysis needed
        self._rec = app.models.get("recognition")
        if self._rec is None:
            for m in app.models.values():
                if hasattr(m, "get_feat"):
                    self._rec = m
                    break
        if self._rec is None:
            raise RuntimeError(
                "ArcFace recognition model not found in buffalo_l. "
                "Check InsightFace installation."
            )
        print("ArcFace recognizer ready (w600k_r50).")

    def get_embedding(self, aligned_face: np.ndarray) -> np.ndarray:
        """
        Extract 512-D L2-normalised embedding from a 112x112 aligned face crop.
        Calls get_feat() directly — bypasses detection entirely.
        """
        if aligned_face is None or aligned_face.size == 0:
            return np.zeros(512, dtype="float32")

        if aligned_face.shape[:2] != (112, 112):
            aligned_face = cv2.resize(aligned_face, (112, 112),
                                      interpolation=cv2.INTER_CUBIC)

        embedding = self._rec.get_feat(aligned_face)
        embedding = np.array(embedding).flatten().astype("float32")
        norm = np.linalg.norm(embedding)
        if norm < 1e-6:
            return np.zeros(512, dtype="float32")
        return embedding / norm

    def get_embeddings_batch(self, face_images: list) -> np.ndarray:
        return np.array([self.get_embedding(img) for img in face_images])


def insightface_align(frame: np.ndarray, kps: np.ndarray) -> np.ndarray:
    """112x112 aligned face using InsightFace's canonical norm_crop."""
    from insightface.utils.face_align import norm_crop
    return norm_crop(frame, kps)
