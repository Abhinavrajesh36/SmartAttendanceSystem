"""
Image Preprocessing Utilities
"""

import cv2
import numpy as np
from typing import Tuple


def preprocess_frame(
    frame: np.ndarray,
    target_size: Tuple[int, int] = None,
    normalize: bool = False
) -> np.ndarray:
    """
    Preprocess video frame
    
    Args:
        frame: Input frame
        target_size: Resize target (optional)
        normalize: Whether to normalize pixel values
        
    Returns:
        Preprocessed frame
    """
    # Convert to RGB if needed
    if len(frame.shape) == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    
    # Resize if target size specified
    if target_size is not None:
        frame = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
    
    # Normalize if requested
    if normalize:
        frame = frame.astype(np.float32) / 255.0
    
    return frame


def enhance_image(image: np.ndarray) -> np.ndarray:
    """
    Enhance image quality
    
    Args:
        image: Input image
        
    Returns:
        Enhanced image
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Split channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    # Merge channels
    enhanced_lab = cv2.merge([l, a, b])
    
    # Convert back to BGR
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    return enhanced


def remove_noise(image: np.ndarray) -> np.ndarray:
    """
    Remove noise from image
    
    Args:
        image: Input image
        
    Returns:
        Denoised image
    """
    denoised = cv2.fastNlMeansDenoisingColored(
        image,
        None,
        h=10,
        hColor=10,
        templateWindowSize=7,
        searchWindowSize=21
    )
    return denoised


def adjust_brightness_contrast(
    image: np.ndarray,
    brightness: int = 0,
    contrast: int = 0
) -> np.ndarray:
    """
    Adjust brightness and contrast
    
    Args:
        image: Input image
        brightness: Brightness adjustment (-100 to 100)
        contrast: Contrast adjustment (-100 to 100)
        
    Returns:
        Adjusted image
    """
    # Adjust brightness
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow
        image = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)
    
    # Adjust contrast
    if contrast != 0:
        alpha_c = 131 * (contrast + 127) / (127 * (131 - contrast))
        gamma_c = 127 * (1 - alpha_c)
        image = cv2.addWeighted(image, alpha_c, image, 0, gamma_c)
    
    return image


def center_crop(
    image: np.ndarray,
    crop_size: Tuple[int, int]
) -> np.ndarray:
    """
    Center crop image
    
    Args:
        image: Input image
        crop_size: Crop dimensions (width, height)
        
    Returns:
        Cropped image
    """
    h, w = image.shape[:2]
    crop_w, crop_h = crop_size
    
    start_x = max(0, (w - crop_w) // 2)
    start_y = max(0, (h - crop_h) // 2)
    
    return image[start_y:start_y + crop_h, start_x:start_x + crop_w]


def augment_image(image: np.ndarray, augment_type: str = 'flip') -> np.ndarray:
    """
    Apply data augmentation
    
    Args:
        image: Input image
        augment_type: Type of augmentation
        
    Returns:
        Augmented image
    """
    if augment_type == 'flip':
        return cv2.flip(image, 1)
    elif augment_type == 'rotate':
        angle = np.random.randint(-15, 15)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, matrix, (w, h))
    elif augment_type == 'brightness':
        value = np.random.randint(-30, 30)
        return adjust_brightness_contrast(image, brightness=value)
    else:
        return image
