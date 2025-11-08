import cv2
import mediapipe as mp
import time

# Initialize mediapipe hands module
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,       # Continuous video stream
    max_num_hands=1,               # Detect one hand
    min_detection_confidence=0.7,  # Detection confidence
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

prev_x = None
gesture = None
last_trigger_time = 0

print("👋 Hand gesture detection started... (Press 'q' to quit)")

while True:
    success, img = cap.read()
    if not success:
        continue

    # Flip the image horizontally for mirror effect
    img = cv2.flip(img, 1)

    # Convert BGR to RGB for mediapipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    h, w, c = img.shape

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            # Draw hand landmarks
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            # Get wrist coordinates
            wrist = handLms.landmark[0]
            wrist_x = int(wrist.x * w)
            wrist_y = int(wrist.y * h)

            # Initialize prev_x
            if prev_x is None:
                prev_x = wrist_x

            # Check movement direction (simple swipe detection)
            diff_x = wrist_x - prev_x
            prev_x = wrist_x

            # Detect swipe right or left
            current_time = time.time()
            if diff_x > 35 and (current_time - last_trigger_time) > 1:
                gesture = "Swipe Right ✋➡️"
                print("👉 Swipe Right detected — Trigger SEND")
                last_trigger_time = current_time

            elif diff_x < -35 and (current_time - last_trigger_time) > 1:
                gesture = "Swipe Left ✋⬅️"
                print("👈 Swipe Left detected — Trigger RECEIVE")
                last_trigger_time = current_time

            # Detect open palm (all fingers extended)
            finger_tips = [8, 12, 16, 20]  # index, middle, ring, pinky tips
            finger_up = 0
            for tip in finger_tips:
                if handLms.landmark[tip].y < handLms.landmark[tip - 2].y:
                    finger_up += 1

            if finger_up == 4 and (current_time - last_trigger_time) > 1:
                gesture = "Open Palm 🖐️"
                print("🖐️ Open Palm detected — Ready to send")
                last_trigger_time = current_time

    # Display gesture on screen
    if gesture:
        cv2.putText(img, f"Gesture: {gesture}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("LinkBeam Gesture Detection", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
