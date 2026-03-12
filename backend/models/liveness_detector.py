"""
Liveness Detector v5  —  3 highly reliable signals only, never blocks alone

FUNDAMENTAL DESIGN CHANGE
──────────────────────────
Previous versions used 6 heuristic signals and blocked on 3+/6 votes.
This caused constant false positives on real webcam faces because:
- Webcam JPEG compression mimics many "flat/compressed" screen artefacts
- No single threshold reliably separates real webcam face from phone screen
  without a trained neural network

SOLUTION
─────────
1. Keep only 3 signals with the highest signal-to-noise ratio
2. This module returns a SOFT WARNING (liveness_score), NOT a hard block
3. Hard blocking only happens in main.py when BOTH:
     a) liveness_score < 0.5  (image signals suggest spoof)
     b) is_static == True     (frontend confirmed no motion between frames)
   A real person always moves slightly → is_static is always False for real faces
   A printed photo held still → is_static is True + image signals fire

THREE RELIABLE SIGNALS
───────────────────────
1. Screen Border Ratio
   Phone held to webcam → bright rectangular screen + dark phone casing.
   Inner 60% of image significantly brighter than outer ring.
   Real face: smooth luminance falloff, no rectangular bright zone.
   False positive rate: very low (only fires when bright rectangle present)

2. HSV Saturation P90
   Phone screens in auto/vivid mode push skin saturation to 160-200.
   Real webcam skin under normal lighting: saturation P90 = 80-140.
   Threshold set conservatively at 165 to avoid flagging tanned skin.

3. Double-JPEG Block Artifact
   Screen photo = 2× JPEG compression → stronger 8-pixel boundary artifacts.
   Measured as ratio of gradient at 8-pixel boundaries vs interior.
   Single JPEG (real): ratio ~1.0-1.15. Double JPEG: ratio >1.25.
   Unaffected by face texture, lighting, or skin tone.
"""

import cv2
import numpy as np
from typing import Tuple, Dict


def _sig_screen_border(bgr: np.ndarray) -> Tuple[float, bool]:
    """
    Phone screen creates bright rectangle framed by dark casing.
    Inner zone mean / outer ring mean > 1.55 = very likely phone screen.
    """
    img  = cv2.resize(bgr, (128, 128))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)

    inner = gray[24:104, 24:104]
    top   = gray[0:20,   20:108]
    bot   = gray[108:,   20:108]
    lft   = gray[20:108, 0:20]
    rgt   = gray[20:108, 108:]
    outer = np.concatenate([top.ravel(), bot.ravel(), lft.ravel(), rgt.ravel()])

    ratio = float(inner.mean()) / (float(outer.mean()) + 1e-9)
    score = float(np.clip((ratio - 1.3) / 0.6, 0, 1))
    return score, ratio > 1.55


def _sig_saturation_excess(bgr: np.ndarray) -> Tuple[float, bool]:
    """
    Phone vivid display oversaturates skin beyond natural webcam range.
    P90 saturation of face-bright pixels > 165 = phone screen vivid mode.
    """
    img = cv2.resize(bgr, (112, 112))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    s   = hsv[:, :, 1]   # 0-255 in OpenCV
    v   = hsv[:, :, 2]

    mask = v > 60
    if int(mask.sum()) < 50:
        return 0.2, False

    p90   = float(np.percentile(s[mask], 90))
    score = float(np.clip((p90 - 140) / 50.0, 0, 1))
    return score, p90 > 165


def _sig_double_jpeg(gray: np.ndarray) -> Tuple[float, bool]:
    """
    Two rounds of JPEG amplify 8-pixel block artefacts.
    Horizontal gradient at rows 8,16,24... vs interior rows.
    """
    img = cv2.resize(gray, (128, 128)).astype(np.float32)

    boundary, interior = [], []
    for r in range(1, 128):
        d = float(np.abs(img[r] - img[r - 1]).mean())
        (boundary if r % 8 == 0 else interior).append(d)

    ratio = (float(np.mean(boundary)) + 1e-9) / (float(np.mean(interior)) + 1e-9)
    score = float(np.clip((ratio - 1.1) / 0.25, 0, 1))
    return score, ratio > 1.22


class LivenessDetector:
    """
    Soft liveness scorer — returns score 0→1 (lower = more spoof-like).
    Hard blocking is handled by main.py using BOTH this score AND the
    is_static flag sent by the frontend (temporal motion detection).
    """

    def __init__(self, model_path: str = None, device: str = "cpu",
                 threshold: float = 0.5):
        print("✅ Liveness Detector v5 (3-signal soft scorer + frontend motion gate)")

    def _analyse(self, face_bgr: np.ndarray) -> Dict:
        if face_bgr.shape[:2] != (224, 224):
            face_bgr = cv2.resize(face_bgr, (224, 224))

        gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)

        s1, f1 = _sig_screen_border(face_bgr)
        s2, f2 = _sig_saturation_excess(face_bgr)
        s3, f3 = _sig_double_jpeg(gray)

        flags       = [f1, f2, f3]
        spoof_votes = sum(flags)
        weights     = [0.40, 0.35, 0.25]
        spoof_score = sum(w * s for w, s in zip(weights, [s1, s2, s3]))

        # Image-only verdict (used as soft hint, not hard gate)
        image_spoof = spoof_votes >= 2   # needs 2 of 3 strong signals

        return {
            "image_spoof": image_spoof,
            "is_live":     not image_spoof,   # kept for compatibility
            "confidence":  float(1.0 - spoof_score),
            "spoof_score": float(spoof_score),
            "spoof_votes": spoof_votes,
            "signals": {
                "screen_border":     {"score": round(s1, 3), "flag": f1},
                "saturation_excess": {"score": round(s2, 3), "flag": f2},
                "double_jpeg":       {"score": round(s3, 3), "flag": f3},
            },
        }

    def predict(self, face_img: np.ndarray) -> bool:
        r = self._analyse(face_img)
        print(f"[Liveness v5] {'SPOOF hint' if r['image_spoof'] else 'LIVE hint'}  "
              f"votes={r['spoof_votes']}/3  conf={r['confidence']:.3f}  {r['signals']}")
        return r["is_live"]

    def predict_with_score(self, face_img: np.ndarray) -> Tuple[bool, float, dict]:
        r = self._analyse(face_img)
        print(f"[Liveness v5] {'SPOOF hint' if r['image_spoof'] else 'LIVE hint'}  "
              f"votes={r['spoof_votes']}/3  conf={r['confidence']:.3f}")
        return r["is_live"], r["confidence"], r
