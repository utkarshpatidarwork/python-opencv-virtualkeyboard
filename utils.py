import cv2
import time

def generate_key_positions(keys, key_size, start_x=10, start_y=10, screen_width=1280):
    """Generate key positions for keyboard layout."""
    key_positions = []
    for row_idx, row in enumerate(keys):
        row_y = start_y + row_idx * (key_size + 10)
        row_length = len(row)
        row_width = row_length * (key_size + 10) - 10
        offset_x = (screen_width - row_width) // 2
        for col_idx, key in enumerate(row):
            col_x = offset_x + col_idx * (key_size + 10)
            key_positions.append((key, col_x, row_y))
    return key_positions

def draw_keys(frame, key_positions, key_size):
    """Draw keyboard buttons on frame."""
    for key, x, y in key_positions:
        cv2.rectangle(frame, (x, y), (x + key_size, y + key_size), (100, 100, 100), 2)
        text = key if key != "SPACE" else "␣"
        cv2.putText(frame, text, (x + 5, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def detect_pressed_key(fingertip, key_positions, key_size, typed_text, last_key, last_time):
    """Detect pressed key based on fingertip position."""
    x_tip, y_tip = fingertip
    now = time.time()
    for key, x, y in key_positions:
        if x < x_tip < x + key_size and y < y_tip < y + key_size:
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
    return key, typed_text, last_key, last_time

def draw_typed_text(frame, typed_text):
    """Draw last 2 lines of typed text on screen."""
    lines = typed_text.split("\n")
    for i, line in enumerate(lines[-2:]):
        y_offset = 650 + i * 25
        cv2.putText(frame, line, (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

def get_suggestions(current_word):
    """Simple word suggestion system."""
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
