import cv2
import mediapipe as mp
import time
import mediapipe as mp


cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpdraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

while True:
    success, img = cap.read()

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    #print(results.multi_hand_landmarks)

    # ...

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                #print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                print(id, cx, cy)
                #if id == 0:
                cv2.circle(img, (cx, cy), 25, (255, 0, 255), cv2.FILLED)

            mpdraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Hand Detection", img)
    cv2.waitKey(1)


'''
# Initialize MediaPipe Face Detection and Face Mesh (Landmark Detection) models.
face_detector = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.5)
face_landmarker = mp.solutions.face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Create a MediaPipe drawing utils object for drawing the detection and landmarks.
drawing_utils = mp.solutions.drawing_utils

# Open a video capture object for the default camera.
cap = cv2.VideoCapture(0)

# Loop over the video frames.
while cap.isOpened():
    # Read a frame from the video capture object.
    ret, frame = cap.read()

    # If the frame is successfully captured, process it.
    if ret:
        # Convert the frame to RGB as required by MediaPipe.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces in the frame.
        face_detection_results = face_detector.process(rgb_frame)

        # Process the frame for landmarks separately to ensure accuracy.
        landmark_results = face_landmarker.process(rgb_frame)

        # If at least one face is detected, draw bounding boxes around them.
        if face_detection_results.detections:
            for detection in face_detection_results.detections:
                drawing_utils.draw_detection(frame, detection)

        # If face landmarks are detected, draw them.
        if landmark_results.multi_face_landmarks:
            for face_landmarks in landmark_results.multi_face_landmarks:
                drawing_utils.draw_landmarks(frame, face_landmarks, mp.solutions.face_mesh.FACEMESH_CONTOURS,
                                             landmark_drawing_spec=None, connection_drawing_spec=mp.solutions.drawing_styles
                                             .get_default_face_mesh_contours_style())

        # Display the processed frame.
        cv2.imshow('MediaPipe Face Detection and Landmarks', frame)

        # Press 'q' to quit the loop and end the program.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the video capture object and close OpenCV windows.
cap.release()
cv2.destroyAllWindows()

'''