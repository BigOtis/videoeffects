import cv2
import mediapipe as mp

def face_tracking_filter(frame, overlay_image_path):
    # Initialize MediaPipe Face Detection
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    overlay_image = cv2.imread(overlay_image_path, cv2.IMREAD_UNCHANGED)
    h, w = frame.shape[:2]

    # Process frame with Face Detection
    results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Check if any face is detected
    if results.detections:
        for detection in results.detections:
            # Get bounding box coordinates
            bboxC = detection.location_data.relative_bounding_box
            bbox = int(bboxC.xmin * w), int(bboxC.ymin * h), \
                   int(bboxC.width * w), int(bboxC.height * h)

            # Overlay size and position (adjust based on your requirements)
            overlay_width = bbox[2]
            overlay_height = bbox[3]
            overlay_x = bbox[0]
            overlay_y = bbox[1]

            # Resize overlay to fit on the face
            resized_overlay = cv2.resize(overlay_image, (overlay_width, overlay_height))

            # Overlay the image on the frame (handle transparency if present)
            for i in range(overlay_height):
                for j in range(overlay_width):
                    # Check if the overlay coordinates are within the frame
                    if 0 <= overlay_y + i < h and 0 <= overlay_x + j < w:
                        if resized_overlay[i, j][3] > 0:  # Alpha channel
                            frame[overlay_y + i, overlay_x + j] = resized_overlay[i, j][:3]

    # Release resources
    face_detection.close()

    return frame
