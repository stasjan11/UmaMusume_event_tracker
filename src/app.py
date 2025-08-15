import sys
import os
import pyautogui
import numpy as np
import easyocr
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QTextCursor, QPixmap
from ui_main import Ui_MainWindow
from main import capture_and_recognize, find_event_in_db, events_db, MIN_TEXT_LENGTH

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.reader = easyocr.Reader(['en'])
        self.timer = QTimer()
        self.is_tracking = False
        self.last_event = None  # Для хранения последнего события
        self.last_event_type = None  # Тип последнего события (найдено/не найдено)

        self.setup_connections()

        self.ui.EventHistoryTextEdit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.ui.DebugPicLabel.setScaledContents(True)
        self.ui.DebugPicLabel.setAlignment(Qt.AlignCenter)

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
        self.timer.start(1000)
        self.log_message("=== Трекер запущен ===")
        self.last_event = None  # Сброс при старте
        self.last_event_type = None

    def stop_tracking(self):
        self.is_tracking = False
        self.ui.StartButton.setEnabled(True)
        self.ui.StopButton.setEnabled(False)
        self.timer.stop()
        self.log_message("=== Трекер остановлен ===")

    def check_events(self):
        if not self.is_tracking:
            return

        try:
            recognized_text = capture_and_recognize()
            self.update_debug_image()

            if len(recognized_text) < MIN_TEXT_LENGTH:
                if self.last_event_type != "short_text":
                    #self.log_message("[!] Слишком мало текста для анализа")
                    self.last_event_type = "short_text"
                return

            event_name = find_event_in_db(recognized_text)

            if event_name:
                if self.last_event != event_name:
                    self.show_event_details(event_name)
                    self.last_event = event_name
                    self.last_event_type = "found"
            else:
                if self.last_event_type != "not_found":
                    #self.log_message("[!] Событие не найдено в базе")
                    self.last_event_type = "not_found"
                    self.last_event = None

        except Exception as e:
            if str(e) != self.last_event:  # Не выводим повторяющиеся ошибки
                self.log_message(f"[ОШИБКА] {str(e)}")
                self.last_event = str(e)
                self.last_event_type = "error"

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

    def show_event_details(self, event_name):
        self.log_message(f"\n[+] Найдено событие: {event_name}")

        if event_name in events_db:
            event_data = events_db[event_name]
            for option in event_data.get("options", []):
                self.log_message(f"\n{option.get('name', 'Без названия')}:")
                for effect in option.get("effects", []):
                    self.log_message(f"  • {effect}")

    def go_back(self):
        self.log_message("\n=== Возврат ===")

    def toggle_event_box_top(self):
        is_top = self.windowFlags() & Qt.WindowStaysOnTopHint
        new_flags = self.windowFlags() ^ Qt.WindowStaysOnTopHint
        self.setWindowFlags(new_flags)
        self.show()
        self.log_message(f"\nРежим 'Поверх других окон': {'включен' if not is_top else 'выключен'}")

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