import mediapipe as mp

# Initialize MediaPipe Selfie Segmentation
mp_selfie_segmentation = mp.solutions.selfie_segmentation
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

def blur_background(frame):
    # Convert the color space from BGR to RGB and process the frame with MediaPipe
    results = selfie_segmentation.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Generate a binary mask using the segmentation results
    condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1
    
    # Apply a Gaussian blur to the entire frame
    blurred_image = cv2.GaussianBlur(frame, (55, 55), 0)

    # Combine the original frame and the blurred frame using the mask
    output_image = np.where(condition, frame, blurred_image)

    return output_image