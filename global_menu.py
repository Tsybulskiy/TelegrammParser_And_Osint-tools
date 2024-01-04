from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QMainWindow, QDialog
from Telegram.TelegramMenu_And_Login import LoginWindow_Telegram, Menu_Telegram
from OsintTools.osint import Menu_Osint
class Menu(QMainWindow):
    def __init__(self):
        super(Menu, self).__init__()

        self.setWindowTitle("Меню")
        self.setGeometry(100, 100, 200, 200)

        self.telegram_button = QPushButton("Парсер Телеграмм", self)
        self.telegram_button.clicked.connect(self.open_telegram_parser)
        self.osint_button = QPushButton("Осинт инструменты", self)
        self.osint_button.clicked.connect(self.open_osint_tools)
        self.osint_window=Menu_Osint()
        self.telegram_window = LoginWindow_Telegram()
        layout = QVBoxLayout()
        layout.addWidget(self.telegram_button)
        layout.addWidget(self.osint_button)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    def open_telegram_parser(self):
        self.close()
        self.telegram_window.exec()
        if self.telegram_window.result() == QDialog.Accepted:
            self.menu = Menu_Telegram(self.telegram_window.client)
            self.menu.show()
    def open_osint_tools(self):
        self.close()
        self.osint_window.show()