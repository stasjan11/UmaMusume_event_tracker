import json
import pyautogui
import time
import re
import easyocr
import numpy as np
from difflib import SequenceMatcher
from text_utils import clean_text

reader = easyocr.Reader(['en'])

MIN_TEXT_LENGTH = 5
SIMILARITY_THRESHOLD = 0.65

# Загрузка и подготовка базы событий
with open('data/events_db.json', 'r', encoding='utf-8') as f:
    events_db_raw = json.load(f)

# Создаем нормализованную версию базы без пунктуации и в нижнем регистре
events_db = {}
normalized_db = {}
for name, data in events_db_raw.items():
    normalized_name = clean_text(name)
    normalized_db[normalized_name] = data
    events_db[name] = data  # Сохраняем оригинальную базу для отображения

def capture_and_recognize():
    screenshot = pyautogui.screenshot(region=(245, 190, 370, 55))
    screenshot.save("debug/latest_screenshot.png")

    # Конвертируем PIL Image в numpy array для EasyOCR
    screenshot_np = np.array(screenshot)

    # Улучшенные параметры распознавания
    results = reader.readtext(
        screenshot_np,
        paragraph=True,
        text_threshold=0.6,
        link_threshold=0.4,
        decoder='beamsearch'
    )

    text = ' '.join([res[1] for res in results]) if results else ''
    return clean_text(text)

def normalize_text(text):
    """Нормализует текст для сравнения - удаляет пунктуацию, приводит к нижнему регистру"""
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).lower().strip()

def find_event_in_db(text):
    # Проверяем длину текста перед обработкой
    if len(text) < MIN_TEXT_LENGTH:
        return "not_enough_chars"

    cleaned_text = clean_text(text)
    print(f"Очищенный текст для поиска: {cleaned_text}")

    best_match = None
    best_score = 0

    for original_name in events_db:
        normalized_name = clean_text(original_name)

        # Метод 1: Сравнение строк с помощью SequenceMatcher
        ratio = SequenceMatcher(None, cleaned_text, normalized_name).ratio()

        # Метод 2: Сравнение по совпадению слов
        cleaned_words = set(cleaned_text.split())
        name_words = set(normalized_name.split())
        word_score = len(cleaned_words & name_words) / len(name_words)

        # Комбинированный score (можно настроить веса)
        combined_score = (ratio * 0.6) + (word_score * 0.4)

        # Если текущий результат лучше предыдущего и превышает порог
        if combined_score > SIMILARITY_THRESHOLD and combined_score > best_score:
            best_score = combined_score
            best_match = original_name
            print(f"Найдено совпадение: {original_name} (score: {combined_score:.2f})")

    return best_match if best_score > 0 else None

def main():
    print("Трекер запущен. Ожидание событий...")
    print(f"Используемый порог схожести: {SIMILARITY_THRESHOLD}")

    while True:
        recognized_text = capture_and_recognize()
        print(f"\nРаспознанный текст: {recognized_text}")

        # Проверяем длину текста
        if len(recognized_text) < MIN_TEXT_LENGTH:
            print("[!] Распознано недостаточно символов для анализа (меньше 5)")
            time.sleep(3)
            continue

        event_name = find_event_in_db(recognized_text)

        if event_name == "not_enough_chars":
            print("[!] После очистки осталось недостаточно символов для анализа")
        elif event_name:
            print(f"\n[+] Найдено событие: {event_name}")
            for option in events_db[event_name]["options"]:
                print(f"\n{option['name']}:")
                for effect in option["effects"]:
                    print(f"  {effect}")
        else:
            print("[!] Событие не распознано или отсутствует в базе.")
            #print("Попробуйте увеличить регион захвата или проверить базу данных.")

        time.sleep(1)

if __name__ == "__main__":
    main()