"""
Face Alignment Utility
======================
CORRECT PIPELINE (fixes wrong-person attendance bug):

The root cause of the "always marks last registered user" bug was that
detect_landmarks_real() was called on the FULL FRAME instead of on a
pre-cropped face region.

Why this matters:
- Registration photos: face fills ~80% of the uploaded image
  -> landmarks at e.g. (55, 40) in a 112x112 image
- Attendance webcam frames: face fills ~30% of a 640x480 frame
  -> same physical face has landmarks at e.g. (210, 145) in a 640x480 image

These two affine warps produce completely different 112x112 outputs for the
SAME physical face. The stored embedding (registration) and query embedding
(attendance) are then far apart in cosine space, causing wrong matches.

SOLUTION - get_aligned_face() (single canonical function for both pipelines):
  1. Crop face bbox with margin -> face_crop (any size)
  2. Resize face_crop to target_size (112x112) -> normalized size
  3. Run landmark detection on THIS normalized crop (coords always in 112x112 space)
  4. If landmarks found: affine warp within 112x112 space (minor correction)
  5. If not: return the resized crop directly

Using this function in BOTH registration and mark-attendance guarantees
identical geometric pipelines -> consistent embeddings.
"""

import cv2
import numpy as np
from typing import Tuple, Optional


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_aligned_face(
    image: np.ndarray,
    bbox: Tuple[int, int, int, int],
    target_size: Tuple[int, int] = (112, 112),
    margin: float = 0.2,
) -> np.ndarray:
    """
    Canonical face alignment used in BOTH registration and mark-attendance.

    Steps:
      1. Expand bbox by `margin` and crop from full image.
      2. Resize crop to `target_size`  <- normalises landmark coordinates.
      3. Run landmark detection on the resized crop.
      4. If landmarks found, apply affine warp within target_size space.
      5. Otherwise return the resized crop directly.

    Using this function in both pipelines ensures the stored embedding and
    the query embedding are produced by the same geometric transformation.

    Args:
        image:       Full frame (BGR).
        bbox:        Bounding box (x1, y1, x2, y2) from face detector.
        target_size: Output (width, height). Use (112,112) for ArcFace.
        margin:      Fraction of bbox size to add as border (default 0.2).

    Returns:
        BGR image of shape (target_size[1], target_size[0], 3), dtype uint8.
    """
    face_crop = _crop_face(image, bbox, margin)
    if face_crop is None:
        return np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)

    # Resize to target size first - landmark coords now always in target_size space
    face_resized = cv2.resize(face_crop, target_size, interpolation=cv2.INTER_CUBIC)

    landmarks = detect_landmarks_real(face_resized)
    if landmarks is not None:
        return align_face_with_landmarks(face_resized, landmarks, target_size)

    return face_resized


def align_face(
    image: np.ndarray,
    bbox: Tuple[int, int, int, int],
    target_size: Tuple[int, int] = (112, 112),
    margin: float = 0.2,
) -> np.ndarray:
    """
    Simple bbox crop + resize WITHOUT landmark alignment.

    Use for: liveness detection crops (224x224) or debug.
    Do NOT use for ArcFace embedding generation - use get_aligned_face().

    Args:
        image:       Full frame (BGR).
        bbox:        Bounding box (x1, y1, x2, y2).
        target_size: Output (width, height).
        margin:      Border fraction.

    Returns:
        BGR image of shape (target_size[1], target_size[0], 3).
    """
    face_crop = _crop_face(image, bbox, margin)
    if face_crop is None:
        return np.zeros((target_size[1], target_size[0], 3), dtype=np.uint8)
    return cv2.resize(face_crop, target_size, interpolation=cv2.INTER_CUBIC)


def detect_landmarks_real(face_crop: np.ndarray) -> Optional[np.ndarray]:
    """
    Detect 5 facial key-points using MediaPipe FaceMesh.

    IMPORTANT: Call this on an ALREADY-CROPPED and RESIZED face image,
    NOT on the full frame. This ensures landmark pixel coordinates are
    always in a normalised (target_size) space.

    Args:
        face_crop: BGR image of the cropped + resized face region.

    Returns:
        ndarray shape (5, 2) float32 - left eye, right eye, nose tip,
        left mouth corner, right mouth corner - in pixel coords within face_crop.
        Returns None if MediaPipe is not installed or no face is found.
    """
    try:
        import mediapipe as mp
    except ImportError:
        return None

    mp_face_mesh = mp.solutions.face_mesh
    try:
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.4,
        ) as mesh:
            rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            results = mesh.process(rgb)

            if not results.multi_face_landmarks:
                return None

            h, w = face_crop.shape[:2]
            lm = results.multi_face_landmarks[0].landmark

            # 5 canonical InsightFace / ArcFace reference indices (FaceMesh 468-point model)
            pts = np.array(
                [
                    [lm[33].x * w,  lm[33].y * h],   # left eye centre
                    [lm[263].x * w, lm[263].y * h],   # right eye centre
                    [lm[1].x * w,   lm[1].y * h],     # nose tip
                    [lm[61].x * w,  lm[61].y * h],    # left mouth corner
                    [lm[291].x * w, lm[291].y * h],   # right mouth corner
                ],
                dtype=np.float32,
            )
            return pts

    except Exception:
        return None


def align_face_with_landmarks(
    face_crop: np.ndarray,
    landmarks: np.ndarray,
    target_size: Tuple[int, int] = (112, 112),
) -> np.ndarray:
    """
    Apply affine warp to a pre-cropped face image using 5-point landmarks.

    Both `face_crop` and `landmarks` must already be in target_size space
    (i.e. detect_landmarks_real must be called AFTER resizing to target_size).

    Args:
        face_crop:   Already-cropped and resized face image (BGR).
        landmarks:   (5, 2) float32 points from detect_landmarks_real().
        target_size: Output (width, height). Must match face_crop dimensions.

    Returns:
        Affine-warped BGR image of shape (target_size[1], target_size[0], 3).
    """
    # InsightFace / ArcFace reference coordinates at 112x112
    reference_112 = np.array(
        [
            [38.2946, 51.6963],   # left eye
            [73.5318, 51.5014],   # right eye
            [56.0252, 71.7366],   # nose tip
            [41.5493, 92.3655],   # left mouth corner
            [70.7299, 92.2041],   # right mouth corner
        ],
        dtype=np.float32,
    )

    # Scale reference if target_size differs from 112x112
    scale_x = target_size[0] / 112.0
    scale_y = target_size[1] / 112.0
    reference = reference_112 * np.array([scale_x, scale_y], dtype=np.float32)

    tform, _ = cv2.estimateAffinePartial2D(landmarks, reference, method=cv2.LMEDS)

    if tform is None:
        # Warp estimation failed - return the resized crop as-is
        return cv2.resize(face_crop, target_size, interpolation=cv2.INTER_CUBIC)

    aligned = cv2.warpAffine(
        face_crop,
        tform,
        target_size,
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REFLECT,
    )
    return aligned


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _crop_face(
    image: np.ndarray,
    bbox: Tuple[int, int, int, int],
    margin: float = 0.2,
) -> Optional[np.ndarray]:
    """Crop face region from image with margin expansion."""
    x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    w, h = x2 - x1, y2 - y1

    if w <= 0 or h <= 0:
        return None

    mx = int(w * margin)
    my = int(h * margin)

    x1 = max(0, x1 - mx)
    y1 = max(0, y1 - my)
    x2 = min(image.shape[1], x2 + mx)
    y2 = min(image.shape[0], y2 + my)

    crop = image[y1:y2, x1:x2]
    if crop.size == 0:
        return None
    return crop
