import re

def clean_text(text):
    # Удаляем спецсимволы и лишние пробелы
    text = re.sub(r'[^\w\s]', '', text)  # Оставляем только буквы и пробелы
    text = re.sub(r'\n', ' ', text)      # Заменяем переносы строк на пробелы
    text = ' '.join(text.split())         # Удаляем двойные пробелы
    return text.strip().lower()