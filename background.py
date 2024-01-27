import mediapipe as mp
import cv2
import numpy as np

# Initialize MediaPipe Selfie Segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

# Buffer for masks
mask_buffer = []
buffer_size = 5  # Number of frames to keep in the buffer

def process_frame_for_mask(frame, scale=0.5, threshold=0.6, use_buffer=True):
    global mask_buffer
    h, w = frame.shape[:2]
    kernel_size = int(0.1 * min(h, w)) | 1  # Ensure kernel size is odd

    # Resize for performance
    small_frame = cv2.resize(frame, (int(w * scale), int(h * scale)))

    # Process with MediaPipe
    results = selfie_segmentation.process(cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB))

    # Generate mask and resize to original dimensions
    mask = results.segmentation_mask > threshold
    mask = mask.astype(np.float32)
    mask = cv2.resize(mask, (w, h))

    # Feather edges
    mask_blurred = cv2.GaussianBlur(mask, (kernel_size, kernel_size), 0)

    # Update buffer
    if use_buffer:
        mask_buffer.append(mask_blurred)
        if len(mask_buffer) > buffer_size:
            mask_buffer.pop(0)
        # Use average of buffered masks
        mask_blurred = np.mean(mask_buffer, axis=0)

    return mask_blurred

def blur_background(frame):
    mask_blurred = process_frame_for_mask(frame)

    # Apply Gaussian blur to the entire frame
    h, w = frame.shape[:2]
    kernel_size = int(0.1 * min(h, w)) | 1
    blurred_frame = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)

    # Combine original frame and blurred frame using the feathered mask
    mask_3d = np.stack((mask_blurred,) * 3, axis=-1)
    output_image = np.where(mask_3d > 0.5, frame, blurred_frame)

    return output_image

def greenscreen_background(frame):
    mask_blurred = process_frame_for_mask(frame)

    # Create a green screen background
    green_background = np.full(frame.shape, (0, 255, 0), dtype=np.uint8)

    # Combine original frame and green background using the feathered mask
    mask_3d = np.stack((mask_blurred,) * 3, axis=-1)
    output_image = np.where(mask_3d > 0.5, frame, green_background)

    return output_image
