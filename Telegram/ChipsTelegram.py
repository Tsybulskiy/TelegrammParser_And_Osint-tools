import pytz
from PyQt5.QtWidgets import QMainWindow, QListWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget, QMessageBox, \
    QListWidgetItem
from phonenumbers import geocoder, carrier, parse
omsk_timezone = pytz.timezone('Asia/Omsk')


class Chips(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setGeometry(100, 100, 500, 600)
        self.setWindowTitle("Small Functions")

        self.chat_list = QListWidget(self)
        self.getchat_button = QPushButton("Получить список чатов")
        self.getchat_button.clicked.connect(self.get_chat)

        self.label2 = QLabel("@username пользователя:", self)
        self.userbox = QLineEdit(self)
        self.user_button = QPushButton("Получить информацию")
        self.user_button.clicked.connect(self.users_info)
        self.user_info = QListWidget(self)

        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)

        layout = QVBoxLayout()
        layout.addWidget(self.getchat_button)
        layout.addWidget(self.chat_list)
        layout.addWidget(self.label2)
        layout.addWidget(self.userbox)
        layout.addWidget(self.user_button)
        layout.addWidget(self.user_info)

        layout.addWidget(self.logout_button)

        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def get_chat(self):
        try:
            user_chats = self.client.get_dialogs()
            for chat in user_chats:
                if chat.is_group:
                    chat_title = chat.name
                elif chat.is_user:
                    chat_title = chat.entity.username
                elif chat.is_channel:
                    chat_title = chat.title
                else:
                    chat_title = "Unknown chat type"

                self.chat_list.addItem(chat_title)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def users_info(self):
        try:
            users = self.userbox.text().split(",")
            for user in users:
                try:
                    info = self.client.get_entity(user)
                    user_id = info.id
                    user_username = info.username
                    user_first_name = info.first_name
                    user_last_name = info.last_name
                    user_telephone = info.phone
                    try:
                        user_online = info.status.was_online.astimezone(omsk_timezone)
                    except:
                        user_online = None
                    if user_telephone:
                        ch_number = parse(f"+{user_telephone}", "CH")
                        ro_number = parse(f"+{user_telephone}", "RO")
                        country = geocoder.description_for_number(ch_number, "ru")
                        user_carrier = carrier.name_for_number(ro_number, "en")
                    else:
                        user_telephone = 'Нет'
                        country = 'Нет'
                        user_carrier = 'Нет'
                    data = QListWidgetItem(
                        f"{user_id} - {user_username} - {user_first_name} - {user_last_name} - {user_last_name} - {user_telephone} - {country} - {user_carrier} - {user_online}",
                        self.user_info)

                    self.user_info.addItem(data)
                except Exception as e:
                    self.user_info.addItem(f"Неккоретно введден пользователь  {user}")
        except Exception as e:
            self.user_info.addItem(f"Неккоретно введден пользователь {user}: ")

    def logout(self):
        self.close()
        from Telegram.TelegramMenu_And_Login import  Menu_Telegram
        self.menu = Menu_Telegram(self.client)
        self.menu.show()