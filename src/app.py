import sys
import os
import pyautogui
import numpy as np
import easyocr
from PySide6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QStyledItemDelegate, QStyle, QLabel
from PySide6.QtCore import QTimer, Qt, QSize, QRect
from PySide6.QtGui import QTextCursor, QPixmap, QIcon, QPainter
from ui_main import Ui_MainWindow
from main import capture_and_recognize, find_event_in_db, events_db, MIN_TEXT_LENGTH

class IconTextDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        # Рисуем иконку и текст
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

        # Рисуем иконку
        icon_rect = QRect(option.rect.x() + 5,
                         option.rect.y() + (option.rect.height() - self.icon_size.height()) // 2,
                         self.icon_size.width(),
                         self.icon_size.height())
        icon.paint(painter, icon_rect, Qt.AlignCenter)

        # Рисуем текст
        text_rect = QRect(icon_rect.right() + 10,
                         option.rect.y(),
                         option.rect.width() - icon_rect.width() - 15,
                         option.rect.height())
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(72)  # Высота элемента (64 + padding)
        return size

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
        self.ui.comboBox.setItemDelegate(IconTextDelegate(self.ui.comboBox))

        self.setup_connections()

        self.ui.EventHistoryTextEdit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.ui.DebugPicLabel.setScaledContents(True)
        self.ui.DebugPicLabel.setAlignment(Qt.AlignCenter)
        self.Sub_Database = None  # Переменная для хранения выбранной базы
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

    def setup_combobox(self):
        images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Uma_Images"))
        icon_size = QSize(64, 64)

        # Установка делегата
        self.ui.comboBox.setItemDelegate(ComboBoxDelegate(self.ui.comboBox))
        self.ui.comboBox.setIconSize(icon_size)

        # Подключение сигнала
        self.ui.comboBox.currentIndexChanged.connect(self.on_combobox_changed)

        self.ui.comboBox.addItem("Выберите базу данных", None)  # None - специальное значение

        if os.path.exists(images_dir):
            for filename in sorted(os.listdir(images_dir)):
                if filename.lower().endswith('.png'):
                    pixmap = QPixmap(os.path.join(images_dir, filename))
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        icon = QIcon(pixmap)
                        display_name = filename[:-4].replace('_', ' ')
                        self.ui.comboBox.addItem(icon, display_name, filename)

        # Стилизация
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
        # Игнорируем первый пустой элемент
        if index == 0:
            self.Sub_Database = None
            return

        selected_file = self.ui.comboBox.itemData(index)
        if selected_file:
            self.Sub_Database = selected_file.replace('.png', '')
            self.log_message(f"\nВыбрана база: {self.Sub_Database.replace('_', ' ')}")
        else:
            self.Sub_Database = None

    def showEvent(self, event):
        super().showEvent(event)
        # Обновляем отображение после показа окна
        self.update_combobox_display()

    def update_combobox_display(self):
        index = self.ui.comboBox.currentIndex()
        if index >= 0:
            # Создаем QLabel для кастомного отображения
            label = QLabel()
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # Получаем иконку и текст
            icon = self.ui.comboBox.itemIcon(index)
            text = self.ui.comboBox.itemText(index)

            # Создаем QPixmap для совмещения иконки и текста
            pixmap = QPixmap(200, 64)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            # Рисуем иконку
            icon.paint(painter, QRect(0, 0, 64, 64))
            # Рисуем текст
            painter.drawText(QRect(74, 0, 126, 64), Qt.AlignLeft | Qt.AlignVCenter, text)
            painter.end()

            # Устанавливаем QPixmap как отображение
            self.ui.comboBox.setItemIcon(index, QIcon(pixmap))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow()
    window.setWindowTitle("Трекер событий")
    window.show()

    sys.exit(app.exec())