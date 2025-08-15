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

        self.setup_connections()

        self.ui.EventHistoryTextEdit.setLineWrapMode(QPlainTextEdit.NoWrap)
        # Настройка для отображения изображения
        self.ui.DebugPicLabel.setScaledContents(True)  # Масштабирование изображения
        self.ui.DebugPicLabel.setAlignment(Qt.AlignCenter)  # Центрирование

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
            # Захват и распознавание текста (сохраняет скриншот в debug/latest_screenshot.png)
            recognized_text = capture_and_recognize()
            
            # Обновление изображения
            self.update_debug_image()
            
            if len(recognized_text) < MIN_TEXT_LENGTH:
                self.log_message("[!] Слишком мало текста для анализа")
                return

            event_name = find_event_in_db(recognized_text)

            if event_name:
                self.show_event_details(event_name)
            else:
                self.log_message("[!] Событие не найдено в базе")

        except Exception as e:
            self.log_message(f"[ОШИБКА] {str(e)}")
    
    def update_debug_image(self):
        """Обновляет изображение в DebugPicLabel из файла"""
        screenshot_path = "debug/latest_screenshot.png"
        if os.path.exists(screenshot_path):
            pixmap = QPixmap(screenshot_path)
            if not pixmap.isNull():
                # Масштабируем изображение с сохранением пропорций
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
        else:
            self.log_message("[!] Данные о событии не найдены")

    def go_back(self):
        self.log_message("\n=== Возврат ===")

    def toggle_event_box_top(self):
        is_top = self.windowFlags() & Qt.WindowStaysOnTopHint
        new_flags = self.windowFlags() ^ Qt.WindowStaysOnTopHint
        self.setWindowFlags(new_flags)
        self.show()
        self.log_message(f"\nРежим 'Поверх других окон': {'включен' if not is_top else 'выключен'}")

    def log_message(self, message):
        """Добавление сообщения в лог с автопрокруткой"""
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