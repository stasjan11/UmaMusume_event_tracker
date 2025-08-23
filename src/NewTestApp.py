import sys
import os
import json
import pyautogui
import numpy as np
import easyocr
import re
from difflib import SequenceMatcher
from PySide6.QtWidgets import (QApplication, QMainWindow, QPlainTextEdit,
                              QStyledItemDelegate, QStyle, QLabel)
from PySide6.QtCore import QTimer, Qt, QSize, QRect
from PySide6.QtGui import QTextCursor, QPixmap, QIcon, QPainter
from ui_main import Ui_MainWindow

# Инициализация EasyOCR
reader = easyocr.Reader(['en'])

# Константы
MIN_TEXT_LENGTH = 5
SIMILARITY_THRESHOLD = 0.65

def clean_text(text):
    """Очистка текста для сравнения"""
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).lower().strip()

# Загрузка основной базы событий
with open('data/events_db.json', 'r', encoding='utf-8') as f:
    events_db_raw = json.load(f)

# Создаем нормализованную версию базы
events_db = {}
normalized_db = {}
for name, data in events_db_raw.items():
    normalized_name = clean_text(name)
    normalized_db[normalized_name] = data
    events_db[name] = data

class IconTextDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icon_size = QSize(64, 64)

    def paint(self, painter, option, index):
        # Рисуем фон
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        # Получаем иконку и текст
        icon = index.data(Qt.DecorationRole)
        text = index.data(Qt.DisplayRole)

        # Если иконка существует - рисуем ее
        if icon and not icon.isNull():
            icon_rect = QRect(option.rect.x() + 5,
                             option.rect.y() + (option.rect.height() - self.icon_size.height()) // 2,
                             self.icon_size.width(),
                             self.icon_size.height())
            icon.paint(painter, icon_rect, Qt.AlignCenter)
            text_left = icon_rect.right() + 10
        else:
            text_left = option.rect.x() + 5

        # Рисуем текст
        text_rect = QRect(text_left,
                         option.rect.y(),
                         option.rect.width() - text_left - 5,
                         option.rect.height())
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(72)
        return size

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.timer = QTimer()
        self.is_tracking = False
        self.last_event = None
        self.last_event_type = None
        self.Sub_Database = None
        self.ui.comboBox.setItemDelegate(IconTextDelegate(self.ui.comboBox))

        self.setup_connections()
        self.ui.EventHistoryTextEdit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.ui.DebugPicLabel.setScaledContents(True)
        self.ui.DebugPicLabel.setAlignment(Qt.AlignCenter)

        # Настройка начального состояния
        self.ui.StartButton.setEnabled(False)
        self.setup_combobox()

    def setup_connections(self):
        self.ui.StartButton.clicked.connect(self.start_tracking)
        self.ui.StopButton.clicked.connect(self.stop_tracking)
        self.ui.GoBackButton.clicked.connect(self.go_back)
        self.ui.EvemtBoxOnTop.clicked.connect(self.toggle_event_box_top)
        self.timer.timeout.connect(self.check_events)

    def start_tracking(self):
        self.is_tracking = True
        self.ui.StartButton.setEnabled(False)
        self.ui.StopButton.setEnabled(True)
        self.ui.comboBox.setEnabled(False)
        self.timer.start(1000)
        self.log_message("=== Трекер запущен ===")
        self.last_event = None
        self.last_event_type = None

    def stop_tracking(self):
        self.is_tracking = False
        self.ui.StartButton.setEnabled(True)
        self.ui.StopButton.setEnabled(False)
        self.ui.comboBox.setEnabled(True)
        self.timer.stop()
        self.log_message("=== Трекер остановлен ===")

    def check_events(self):
        if not self.is_tracking:
            return

        try:
            recognized_text = self.capture_and_recognize()
            self.update_debug_image()

            if len(recognized_text) < MIN_TEXT_LENGTH:
                if self.last_event_type != "short_text":
                    self.last_event_type = "short_text"
                return

            event_name = self.find_event_in_db(recognized_text, self.Sub_Database)

            if event_name:
                if self.last_event != event_name:
                    self.show_event_details(event_name)
                    self.last_event = event_name
                    self.last_event_type = "found"
            else:
                if self.last_event_type != "not_found":
                    self.log_message("[!] Событие не найдено в базе")
                    self.last_event_type = "not_found"
                    self.last_event = None

        except Exception as e:
            if str(e) != self.last_event:
                self.log_message(f"[ОШИБКА] {str(e)}")
                self.last_event = str(e)
                self.last_event_type = "error"

    def capture_and_recognize(self):
        screenshot = pyautogui.screenshot(region=(245, 190, 370, 55))
        screenshot.save("debug/latest_screenshot.png")
        screenshot_np = np.array(screenshot)

        results = reader.readtext(
            screenshot_np,
            paragraph=True,
            text_threshold=0.6,
            link_threshold=0.4,
            decoder='beamsearch'
        )

        text = ' '.join([res[1] for res in results]) if results else ''
        return clean_text(text)

    def find_event_in_db(self, text, sub_db=None):
        if len(text) < MIN_TEXT_LENGTH:
            return "not_enough_chars"

        cleaned_text = clean_text(text)

        # Сначала проверяем дополнительную базу
        if sub_db:
            sub_db_path = f"data/{sub_db}.json"
            try:
                with open(sub_db_path, 'r', encoding='utf-8') as f:
                    sub_db_data = json.load(f)

                match = self.search_in_database(cleaned_text, sub_db_data)
                if match:
                    return match
            except Exception as e:
                self.log_message(f"[ОШИБКА] Не удалось загрузить базу {sub_db}: {str(e)}")

        # Затем проверяем основную базу
        return self.search_in_database(cleaned_text, events_db)

    def search_in_database(self, text, database):
        best_match = None
        best_score = 0

        for original_name in database:
            normalized_name = clean_text(original_name)

            ratio = SequenceMatcher(None, text, normalized_name).ratio()
            text_words = set(text.split())
            name_words = set(normalized_name.split())
            word_score = len(text_words & name_words) / len(name_words)
            combined_score = (ratio * 0.6) + (word_score * 0.4)

            if combined_score > SIMILARITY_THRESHOLD and combined_score > best_score:
                best_score = combined_score
                best_match = original_name

        return best_match if best_score > 0 else None

    def show_event_details(self, event_name):
        self.log_message(f"\n[+] Найдено событие: {event_name}")

        # Проверяем сначала в дополнительной базе
        if self.Sub_Database:
            try:
                with open(f"data/{self.Sub_Database}.json", 'r', encoding='utf-8') as f:
                    sub_db = json.load(f)
                if event_name in sub_db:
                    self.log_event_options(sub_db[event_name]["options"])
                    return
            except:
                pass

        # Если не найдено, проверяем основную базу
        if event_name in events_db:
            self.log_event_options(events_db[event_name]["options"])
        else:
            self.log_message("[!] Данные о событии не найдены")

    def log_event_options(self, options):
        for option in options:
            self.log_message(f"\n{option.get('name', 'Без названия')}:")
            for effect in option.get("effects", []):
                self.log_message(f"  • {effect}")

    def setup_combobox(self):
        images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Uma_Images"))
        icon_size = QSize(64, 64)

        self.ui.comboBox.setItemDelegate(ComboBoxDelegate(self.ui.comboBox))
        self.ui.comboBox.setIconSize(icon_size)
        self.ui.comboBox.currentIndexChanged.connect(self.on_combobox_changed)

        self.ui.comboBox.addItem("Выберите базу данных", None)

        if os.path.exists(images_dir):
            for filename in sorted(os.listdir(images_dir)):
                if filename.lower().endswith('.png'):
                    pixmap = QPixmap(os.path.join(images_dir, filename))
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        icon = QIcon(pixmap)
                        display_name = filename[:-4].replace('_', ' ')
                        self.ui.comboBox.addItem(icon, display_name, filename[:-4])

        self.ui.comboBox.setStyleSheet("""
            QComboBox {
                padding: 5px 15px;
                min-height: 64px;
                font-size: 14px;
            }
            QComboBox::item {
                height: 64px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                min-width: 250px;
            }
        """)

    def on_combobox_changed(self, index):
        if index == 0:
            self.Sub_Database = None
            self.ui.StartButton.setEnabled(False)
            return

        selected_db = self.ui.comboBox.itemData(index)
        if selected_db:
            self.Sub_Database = selected_db
            self.log_message(f"\nВыбрана база: {selected_db.replace('_', ' ')}")
            self.ui.StartButton.setEnabled(True)
        else:
            self.Sub_Database = None
            self.ui.StartButton.setEnabled(False)

    def update_debug_image(self):
        screenshot_path = "debug/latest_screenshot.png"
        if os.path.exists(screenshot_path):
            pixmap = QPixmap(screenshot_path)
            if not pixmap.isNull():
                self.ui.DebugPicLabel.setPixmap(pixmap.scaled(
                    self.ui.DebugPicLabel.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))

    def go_back(self):
        self.log_message("\n=== Возврат ===")

    def toggle_event_box_top(self):
        is_top = self.windowFlags() & Qt.WindowStaysOnTopHint
        new_flags = self.windowFlags() ^ Qt.WindowStaysOnTopHint
        self.setWindowFlags(new_flags)
        self.show()
        self.log_message(f"\nРежим 'Поверх других окон': {'включен' if not is_top else 'выклюден'}")

    def log_message(self, message):
        self.ui.EventHistoryTextEdit.appendPlainText(message)
        cursor = self.ui.EventHistoryTextEdit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.ui.EventHistoryTextEdit.setTextCursor(cursor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow()
    window.setWindowTitle("Трекер событий")
    window.show()

    sys.exit(app.exec())