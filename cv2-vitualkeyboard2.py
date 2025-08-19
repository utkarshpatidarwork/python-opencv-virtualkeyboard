import cv2
import mediapipe as mp
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Adjusted keyboard layout to fit standard screen (max 1280x720)
keys = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    ["Z", "X", "C", "V", "B", "N", "M", "<-", "SPACE", "ENTER"]
]

key_size = 50  # smaller to fit screen
start_x, start_y = 10, 10

# Generate key positions
key_positions = []
for row_idx, row in enumerate(keys):
    row_y = start_y + row_idx * (key_size + 10)
    row_length = len(row)
    row_width = row_length * (key_size + 10) - 10
    offset_x = (1280 - row_width) // 2  # center horizontally
    for col_idx, key in enumerate(row):
        col_x = offset_x + col_idx * (key_size + 10)
        key_positions.append((key, col_x, row_y))

# Track typing
typed_text = ""
last_key = None
last_time = 0

# Word suggestions
def get_suggestions(current_word):
    suggestions_dict = {
        "he": ["hello", "hey", "help"],
        "th": ["there", "that", "thanks"],
        "yo": ["you", "your", "yours"],
        "": ["hello", "hi", "welcome"],
    }
    for prefix in suggestions_dict:
        if current_word.lower().startswith(prefix):
            return suggestions_dict[prefix]
    return []

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    fingertip = None

    # Draw keys
    for key, x, y in key_positions:
        cv2.rectangle(frame, (x, y), (x + key_size, y + key_size), (100, 100, 100), 2)
        text = key if key != "SPACE" else "␣"
        cv2.putText(frame, text, (x + 5, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Detect fingertip
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            x_tip = int(hand_landmarks.landmark[8].x * w)
            y_tip = int(hand_landmarks.landmark[8].y * h)
            fingertip = (x_tip, y_tip)

            cv2.circle(frame, fingertip, 8, (0, 255, 0), -1)

            for key, x, y in key_positions:
                if x < x_tip < x + key_size and y < y_tip < y + key_size:
                    now = time.time()
                    if last_key == key:
                        if now - last_time > 1.0:
                            if key == "<-":
                                typed_text = typed_text[:-1]
                            elif key == "SPACE":
                                typed_text += " "
                            elif key == "ENTER":
                                typed_text += "\n"
                            else:
                                typed_text += key
                            print(f"Pressed: {key}")
                            last_time = now + 1
                    else:
                        last_key = key
                        last_time = now
                    cv2.rectangle(frame, (x, y), (x + key_size, y + key_size), (0, 255, 0), 3)
                    break
            else:
                last_key = None

    # Draw typed text (last 2 lines)
    lines = typed_text.split("\n")
    for i, line in enumerate(lines[-2:]):
        y_offset = 650 + i * 25
        cv2.putText(frame, line, (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Word suggestions
    last_word = typed_text.strip().split(" ")[-1] if typed_text.strip() else ""
    suggestions = get_suggestions(last_word)
    for i, word in enumerate(suggestions):
        x_sug = w - 250
        y_sug = 50 + i * 30
        cv2.putText(frame, word, (x_sug, y_sug), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)

    cv2.imshow("Virtual Keyboard", frame)
    if cv2.waitKey(1) == 27:
        break

with open("typed_output.txt", "w") as f:
    f.write(typed_text)

cap.release()
cv2.destroyAllWindows()

