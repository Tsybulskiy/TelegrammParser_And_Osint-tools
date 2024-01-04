import csv

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QListWidget, QAbstractItemView, QVBoxLayout, \
    QWidget, QMessageBox, QFileDialog, QListWidgetItem
from phonenumbers import geocoder, carrier, parse
from telethon.tl.types import Channel


class TelegramClosedData(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setGeometry(100, 100, 500, 600)
        self.setWindowTitle("Telegram Close Parser")
        self.label = QLabel("Ссылка на телеграм чат:", self)
        self.label3 = QLabel("Введите количество пользователей", self)
        self.textbox = QLineEdit(self)
        self.limitbox = QLineEdit(self)
        self.button = QPushButton("Запуск", self)
        self.button.clicked.connect(self.close_chat)
        self.load_list = QListWidget(self)
        self.load_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.load_list.itemSelectionChanged.connect(self.show_user_messages)
        self.logout_button = QPushButton("Выход", self)
        self.logout_button.clicked.connect(self.logout)
        self.load_button = QPushButton("Загрузить файл формата CSV", self)
        self.load_button.clicked.connect(self.load_from_csv)
        self.message_list = QListWidget(self)
        self.message_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.search_label = QLabel("Поиск:", self)
        self.search_textbox = QLineEdit(self)
        self.search_textbox.setPlaceholderText("Введите слово для поиска")
        self.search_textbox.textChanged.connect(self.search_items)
        self.search_result_list = QListWidget(self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.textbox)
        layout.addWidget(self.label3)
        layout.addWidget(self.limitbox)
        layout.addWidget(self.button)
        layout.addWidget(self.load_list)
        layout.addWidget(self.load_button)
        layout.addWidget(self.message_list)

        layout.addWidget(self.search_label)
        layout.addWidget(self.search_textbox)
        layout.addWidget(self.search_result_list)
        layout.addWidget(self.logout_button)
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def close_chat(self):

        chat_identifier = self.textbox.text()
        if not chat_identifier:
            QMessageBox.critical(self, "Error", "Введите идентификатор чата.")
            return

        limit = int(self.limitbox.text())
        if not limit:
            QMessageBox.critical(self, "Error", "Введите количество пользователей.")
            return
        entity = None
        entity_cache = {}
        user_data = []

        try:
            if chat_identifier.isdigit():
                entity = self.client.get_entity(int(chat_identifier))
            elif chat_identifier.startswith(("https://", "t.me")):
                entity = self.client.get_entity(chat_identifier)
            else:
                dialogs = self.client.get_dialogs()
                entity = next((dialog.entity for dialog in dialogs if chat_identifier.lower() in dialog.title.lower()),
                              None)

            users_ids = set()
            for message in self.client.iter_messages(chat_identifier, limit=None):
                if len(users_ids) == limit:
                    break
                if message.sender_id in users_ids:
                    continue

                users_ids.add(message.sender_id)
                sender = self.client.get_entity(message.sender_id)
                if isinstance(sender, Channel):
                    limit += 1
                    continue

                if not entity_cache.get(message.sender_id):
                    usernames = self.client.get_entity(message.sender_id)
                    entity_cache[message.sender_id] = usernames

                usernames = entity_cache.get(message.sender_id)
                user_username = usernames.username
                user_first_name = usernames.first_name
                user_last_name = usernames.last_name
                user_telephone = usernames.phone

                if user_telephone:
                    ch_number = parse(f"+{user_telephone}", "CH")
                    ro_number = parse(f"+{user_telephone}", "RO")
                    country = geocoder.description_for_number(ch_number, "ru")
                    user_carrier = carrier.name_for_number(ro_number, "en")
                else:
                    user_telephone = 'Нет'
                    country = 'Нет'
                    user_carrier = 'Нет'

                user_data.append({
                    'User_id': message.sender_id,
                    'Username': user_username,
                    'First Name': user_first_name,
                    'Second Name': user_last_name,
                    'Phone': user_telephone,
                    'Country': country,
                    'Carrier': user_carrier
                })

            options = QFileDialog.Options()
            file_dialog, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "CSV Files (*.csv)",
                                                         options=options)

            if file_dialog:
                filename = file_dialog.split('/')[-1].split('.')[0] + '.csv'
            else:
                return

            with open(f'{file_dialog}', 'w', newline='', encoding='utf-16') as file:
                fieldnames = ['User_id', 'Username', 'First Name', 'Second Name', 'Phone', 'Country', 'Carrier']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerows(user_data)

        except Exception as e:
            if str(e) == "Cannot cast NoneType to any kind of Peer.":
                try:
                    options = QFileDialog.Options()
                    file_dialog, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "CSV Files (*.csv)",
                                                                 options=options)
                    if file_dialog:
                        with open(f'{file_dialog}', 'w', newline='', encoding='utf-16') as file:
                            fieldnames = ['User_id', 'Username', 'First Name', 'Second Name', 'Phone', 'Country',
                                          'Carrier']
                            writer = csv.DictWriter(file, fieldnames=fieldnames)

                            writer.writeheader()
                            writer.writerows(user_data)
                except Exception as e_write:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText(f"Ошибка записи в файл: {str(e_write)}")
                    msg.exec_()
                return
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(f"Ошибка: {str(e)}")
                msg.exec_()

    def load_from_csv(self):
        self.load_list.clear()
        try:
            filename, _ = QFileDialog.getOpenFileName(self, "Load CSV", "", "CSV Files (*.csv)")
            if filename:
                with open(filename, 'r', newline='', encoding='utf-16') as file:
                    reader = csv.reader(file, delimiter=',')
                    for row in reader:
                        values = row
                        try:
                            participant_id = values[0]
                            participant_username = values[1]
                            participant_name = values[2]
                            participant_surname = values[3]
                            participant_telephone = values[4]
                            geoposition = values[5]
                            user_carrier = values[6]
                            item_text = f"{participant_id} - {participant_username} - {participant_name} - {participant_surname} - {participant_telephone} - {geoposition} - {user_carrier}"
                            item = QListWidgetItem(item_text, self.load_list)
                            item.setData(Qt.UserRole, participant_id)
                        except Exception as e:
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Critical)
                            msg.setText(f"Ошибка: {str(e)}")
                            msg.exec_()

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def show_user_messages(self):

        self.message_list.clear()
        chat_link = self.textbox.text()
        if not chat_link:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Введите название чата или ссылку на него")
            msg.exec_()

        all_messages = []

        try:
            entity = self.client.get_entity(chat_link)
            chat_id = entity.id

            for item in self.load_list.selectedItems():
                participant_id = item.data(Qt.UserRole)
                try:
                    participant = self.client.get_entity(int(participant_id))
                    messages = self.client.iter_messages(chat_id, from_user=participant, limit=None)

                    for message in messages:
                        msg_text = message.message
                        msg_date = message.date
                        username = participant.username if participant.username else 'No Username'
                        all_messages.append((msg_date, msg_text, participant_id, username))
                except Exception as e:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText(f"Ошибка: {str(e)}")
                    msg.exec_()

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

        all_messages.sort(key=lambda x: x[0], reverse=True)

        for msg_date, msg_text, participant_id, username in all_messages:
            list_item = QListWidgetItem(
                f"{msg_date.strftime('%Y-%m-%d %H:%M:%S')} - {msg_text} - {participant_id} - {username}",
                self.message_list)
            self.message_list.addItem(list_item)

    def search_items(self):
        search_text = self.search_textbox.text().lower()
        self.search_result_list.clear()
        for list_widget in [self.message_list, self.load_list]:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item_text = item.text().lower()
                if search_text in item_text:
                    self.search_result_list.addItem(item.text())

    def logout(self):
        self.close()
        from TelegramMenu_And_Login import Menu_Telegram
        self.menu = Menu_Telegram(self.client)
        self.menu.show()
