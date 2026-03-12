
"""
YOLOv9 Face Detector Module (FIXED)
Compatible with torch.hub YOLOv9 AutoShape outputs
No manual NMS / tensor parsing
"""

import torch
import cv2
import numpy as np
from typing import List, Tuple
import time


class YOLOv9FaceDetector:
    """
    YOLOv9-based face detector
    Real-time detection using AutoShape outputs
    """

    def __init__(
        self,
        model_path: str,
        conf_threshold: float = 0.35,
        iou_threshold: float = 0.45,
        device: str = "cuda"
    ):
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device

        print(f"Loading YOLOv9 model from {model_path}...")
        self.model = self._load_model(model_path)

        self.model.to(self.device).eval()

        print(f"✅ YOLOv9 Face Detector initialized on {self.device}")

    # ----------------------------------------------------
    # Load YOLOv9 correctly
    # ----------------------------------------------------
    def _load_model(self, model_path: str):

        model = torch.hub.load(
            "WongKinYiu/yolov9",
            "custom",
            path=model_path,
            trust_repo=True
        )

        # set thresholds
        model.conf = self.conf_threshold
        model.iou = self.iou_threshold

        return model

    # ----------------------------------------------------
    # Detect faces (CORRECT)
    # ----------------------------------------------------
    def detect(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in frame using YOLOv9 AutoShape

        Returns:
            List[(x1,y1,x2,y2)]
        """

        # convert BGR -> RGB
        img = frame[:, :, ::-1]

        # inference
        results = self.model(img, size=640)

        detections = []

        if results.xyxy[0] is not None:
            for *box, conf, cls in results.xyxy[0].cpu().numpy():

                x1, y1, x2, y2 = map(int, box)

                detections.append((x1, y1, x2, y2))

        return detections

    # ----------------------------------------------------
    # Batch detect
    # ----------------------------------------------------
    def detect_batch(
        self,
        frames: List[np.ndarray]
    ) -> List[List[Tuple[int, int, int, int]]]:

        results = []
        for frame in frames:
            results.append(self.detect(frame))
        return results

    # ----------------------------------------------------
    # Benchmark
    # ----------------------------------------------------
    def benchmark(self, frame: np.ndarray, num_iterations: int = 100) -> dict:

        print(f"Running benchmark for {num_iterations} iterations...")

        times = []
        for _ in range(num_iterations):
            start = time.time()
            _ = self.detect(frame)
            times.append(time.time() - start)

        avg_time = np.mean(times)

        return {
            "average_time_ms": avg_time * 1000,
            "fps": 1.0 / avg_time,
            "min_time_ms": np.min(times) * 1000,
            "max_time_ms": np.max(times) * 1000,
            "std_time_ms": np.std(times) * 1000
        }


# --------------------------------------------------------
# Test
# --------------------------------------------------------
if __name__ == "__main__":

    detector = YOLOv9FaceDetector(
        model_path="weights/yolov9_face.pt",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )

    img = cv2.imread("test_images/sample.jpg")

    if img is not None:

        boxes = detector.detect(img)
        print("Detected:", len(boxes))

        for (x1, y1, x2, y2) in boxes:
            cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)

        cv2.imwrite("output/detection_result.jpg", img)

        print(detector.benchmark(img))
