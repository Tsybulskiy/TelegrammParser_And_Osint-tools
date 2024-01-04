from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget, QMessageBox, QDialog, QFormLayout, \
    QLineEdit, QApplication
from telethon.sync import TelegramClient

from ChipsTelegram import Chips
from TelegramChatData import TelegramChatData
from TelegramChatParser import TelegramChatParser
from TelegramClosedData import TelegramClosedData

from PacketSniffer import PacketSniffer
class Menu_Telegram(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setWindowTitle("Menu_Telegram")
        self.setGeometry(100, 100, 200, 200)

        layout = QVBoxLayout()

        self.real_time_button = QPushButton("Отслеживание в реальном времени")
        self.real_time_button.clicked.connect(self.open_chat_parser)
        self.data_parser_button = QPushButton("Получение данных из чата")
        self.data_parser_button.clicked.connect(self.open_data_parser)
        self.close_parser_button = QPushButton("Получение данных из закрытого чата")
        self.close_parser_button.clicked.connect(self.close_data_parser)
        self.chips_button = QPushButton("Мелкие функции")
        self.chips_button.clicked.connect(self.chips)
        self.sniffer_button = QPushButton("Получение ip-адреса")
        self.sniffer_button.clicked.connect(self.sniffer)
        self.logout_button = QPushButton("Выход")
        self.logout_button.clicked.connect(self.logout)

        layout.addWidget(self.real_time_button)
        layout.addWidget(self.data_parser_button)
        layout.addWidget(self.close_parser_button)
        layout.addWidget(self.chips_button)
        layout.addWidget(self.sniffer_button)
        layout.addWidget(self.logout_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def sniffer(self):
        try:
            self.sniffer_window = PacketSniffer(self.client)
            self.sniffer_window.show()
            self.close()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def chips(self):
        try:
            self.chips_window = Chips(self.client)
            self.chips_window.show()
            self.close()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def close_data_parser(self):
        try:
            self.chat_parser_window = TelegramClosedData(self.client)
            self.chat_parser_window.show()
            self.close()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def open_chat_parser(self):
        try:
            self.chat_parser_window = TelegramChatParser(self.client)
            self.chat_parser_window.show()
            self.close()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def open_data_parser(self):
        try:
            self.data_parser_window = TelegramChatData(self.client)
            self.data_parser_window.show()
            self.close()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def logout(self):
        try:
            self.client.log_out()
            self.close()
            QMessageBox.information(self, "Logout", "Logged out successfully!")
            from global_menu import Menu
            self.menu = Menu()
            self.menu.show()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()
class LoginWindow_Telegram(QDialog):
    def __init__(self):
        super(LoginWindow_Telegram, self).__init__()

        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 200, 200)

        layout = QFormLayout()

        self.api_id_input = QLineEdit()
        self.api_hash_input = QLineEdit()
        self.phone_number_input = QLineEdit()
        self.code_input = QLineEdit()

        layout.addRow("API ID", self.api_id_input)
        layout.addRow("API Hash", self.api_hash_input)
        layout.addRow("Номер телефона", self.phone_number_input)
        layout.addRow("Код телеграм", self.code_input)

        self.connect_button = QPushButton("Соединение")
        self.connect_button.clicked.connect(self.connect)

        self.send_code_button = QPushButton("Отправить код")
        self.send_code_button.clicked.connect(self.send_code)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login)

        layout.addRow(self.connect_button)
        layout.addRow(self.send_code_button)
        layout.addRow(self.login_button)

        self.setLayout(layout)

        self.client = None

    def closeEvent(self, event):
        QApplication.instance().close()

    def connect(self):
        try:
            self.api_id = self.api_id_input.text()
            self.api_hash = self.api_hash_input.text()
            self.phone_number = self.phone_number_input.text()

            with open('../login_data.txt', 'w') as file:
                file.write(f'{self.api_id},{self.api_hash},{self.phone_number}')

            self.client = TelegramClient('session', self.api_id, self.api_hash, device_model="iPhone 13 Pro Max",
                                         system_version="14.8.1",
                                         app_version="8.4",
                                         lang_code="en",
                                         system_lang_code="en-US")

            self.client.connect()
            if self.client.is_user_authorized():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Вы уже авторизованы.")
                msg.exec_()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Теперь запросите и введите код.")
                msg.exec_()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def send_code(self):
        try:
            if self.client is None or not self.client.is_connected():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Необходимо выполнить соединение перед отправкой кода.")
                msg.exec_()
            elif not self.client.is_user_authorized():
                self.client.send_code_request(self.phone_number)
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Вы уже авторизованы, ввод кода не требуется.")
                msg.exec_()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def login(self):
        try:
            if self.client is None or not self.client.is_connected():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Необходимо выполнить соединение перед входом в аккаунт.")
                msg.exec_()
            elif self.client.is_user_authorized():
                self.accept()
            else:
                input_code = self.code_input.text()

                if input_code:
                    try:
                        self.client.sign_in(self.phone_number, input_code)
                        if self.client.is_user_authorized():
                            self.accept()
                        else:
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Не удалось авторизоваться. Проверьте введенный код.")
                            msg.exec_()
                    except Exception as e:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText("Введен неверный код, попробуйте еще раз.")
                        msg.exec_()
                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Перед входом в аккаунт, пожалуйста, запросите и введите код.")
                    msg.exec_()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def load_saved_data(self):
        try:
            with open('../login_data.txt', 'r') as file:
                data = file.read()
                if data:
                    api_id, api_hash, phone_number = data.split(',')
                    self.api_id_input.setText(api_id)
                    self.api_hash_input.setText(api_hash)
                    self.phone_number_input.setText(phone_number)

        except FileNotFoundError:
            pass

    def showEvent(self, event):
        self.load_saved_data()
        super(LoginWindow_Telegram, self).showEvent(event)