import keyboard
import pyautogui

print("Нажмите 'k' для координат, 'q' для выхода...")

while True:
    event = keyboard.read_event()  # Ждём событие клавиши
    if event.event_type == keyboard.KEY_DOWN:
        if event.name == 'k':
            x, y = pyautogui.position()
            print(f"X={x}, Y={y}")
        elif event.name == 'q':
            break