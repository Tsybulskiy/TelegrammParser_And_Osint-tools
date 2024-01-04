import csv

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem, QMessageBox, QMainWindow, QLabel, QLineEdit, QPushButton, QListWidget, \
    QVBoxLayout, QAbstractItemView, QWidget, QFileDialog
from phonenumbers import geocoder, carrier, parse


class TelegramChatData(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.setGeometry(100, 100, 500, 600)
        self.setWindowTitle("Telegram Chat Parser")

        self.label = QLabel("Ссылка на телеграм чат:", self)
        self.textbox = QLineEdit(self)
        self.button = QPushButton("Запуск", self)
        self.button.clicked.connect(self.parse_chat)
        self.logout_button = QPushButton("Выход", self)
        self.logout_button.clicked.connect(self.logout)
        self.user_list = QListWidget(self)
        self.user_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.user_list.itemSelectionChanged.connect(self.show_user_messages)
        self.message_list = QListWidget(self)

        self.search_label = QLabel("Поиск:", self)
        self.search_textbox = QLineEdit(self)
        self.search_textbox.setPlaceholderText("Введите слово для поиска")
        self.search_textbox.textChanged.connect(self.search_items)
        self.search_result_list = QListWidget(self)

        self.save_button = QPushButton("Сохранить информацию о чате в файл формата CSV", self)
        self.save_button.clicked.connect(self.save_to_csv)
        self.save_button2 = QPushButton("Сохранить сообщения данного пользователя в файл формата CSV", self)
        self.save_button2.clicked.connect(self.save_to_csv2)
        self.load_button = QPushButton("Загрузить файл формата CSV", self)
        self.load_button.clicked.connect(self.load_from_csv)
        self.load_list = QListWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.textbox)
        layout.addWidget(self.button)

        layout.addWidget(self.user_list)
        layout.addWidget(self.message_list)

        search_layout = QVBoxLayout()
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_textbox)
        search_layout.addWidget(self.search_result_list)

        layout.addLayout(search_layout)
        layout.addWidget(self.save_button)
        layout.addWidget(self.save_button2)
        layout.addWidget(self.load_button)
        layout.addWidget(self.load_list)
        layout.addWidget(self.logout_button)

        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def search_items(self):
        search_text = self.search_textbox.text().lower()
        self.search_result_list.clear()
        for list_widget in [self.user_list, self.message_list, self.load_list]:
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item_text = item.text().lower()
                if search_text in item_text:
                    self.search_result_list.addItem(item.text())

    def parse_chat(self):
        self.user_list.clear()
        self.message_list.clear()
        chat_identifier = self.textbox.text()

        try:
            entity = None
            if chat_identifier.isdigit():
                entity = self.client.get_entity(int(chat_identifier))
            else:
                if chat_identifier.startswith("https://") or chat_identifier.startswith("t.me"):
                    entity = self.client.get_entity(chat_identifier)
                else:
                    dialogs = self.client.get_dialogs()
                    for dialog in dialogs:
                        if chat_identifier.lower() in dialog.title.lower():
                            entity = dialog.entity
                            break

            if entity is not None:
                participants = self.client.get_participants(entity)

                for participant in participants:
                    participant_id = participant.id
                    participant_username = participant.username
                    participant_name = participant.first_name
                    participant_surname = participant.last_name
                    participant_telephone = participant.phone
                    if participant_telephone is not None:
                        ch_number = parse(f"+{participant_telephone}", "CH")
                        ro_number = parse(f"+{participant_telephone}", "RO")
                        country = geocoder.description_for_number(ch_number, "ru")
                        user_carrier = carrier.name_for_number(ro_number, "en")

                    else:
                        country = None
                        user_carrier = None
                    item = QListWidgetItem(
                        f"{participant_id} - {participant_username} - {participant_name} - {participant_surname} - {participant_telephone} - {country} - {user_carrier}",
                        self.user_list)
                    item.setData(Qt.UserRole, participant_id)
            else:
                QMessageBox.critical(self, "Error", "Chat not found.")

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def show_user_messages(self):

        self.message_list.clear()
        chat_link = self.textbox.text()

        all_messages = []

        for item in self.user_list.selectedItems():
            participant_id = item.data(Qt.UserRole)
            try:
                participant = self.client.get_entity(int(participant_id))
                messages = self.client.iter_messages(chat_link, from_user=participant, limit=None)

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

        all_messages.sort(key=lambda x: x[0], reverse=True)

        for msg_date, msg_text, participant_id, username in all_messages:
            list_item = QListWidgetItem(
                f"{msg_date.strftime('%Y-%m-%d %H:%M:%S')} - {msg_text} - {participant_id} - {username}",
                self.message_list)
            self.message_list.addItem(list_item)

    def save_to_csv(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
            if filename:

                with open(filename, 'w', newline='', encoding='utf-16') as file:
                    writer = csv.writer(file, delimiter=',')
                    writer.writerow(["ID", "Username", "FirstName", "Last Name", "Telephone", "Geoposition", "Carrier"])
                    for row in range(self.user_list.count()):
                        item = self.user_list.item(row)
                        values = item.text().split(" - ")
                        writer.writerow(values)

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def save_to_csv2(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
            if filename:

                with open(filename, 'w', newline='', encoding='utf-16') as file:
                    writer = csv.writer(file, delimiter=',')
                    writer.writerow(["Date", "Messages", "ID", "Username"])
                    for row in range(self.message_list.count()):
                        item = self.message_list.item(row)
                        values = item.text().split(" - ")
                        writer.writerow(values)

        except Exception as e:
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
                        except:
                            date = values[0]
                            message = values[1]
                            ID = values[2]
                            Username = values[3]
                            item_text = f"{date} - {message} - {ID} - {Username}"
                            item = QListWidgetItem(item_text, self.load_list)
                            item.setData(Qt.UserRole, participant_id)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def logout(self):
        self.close()
        from TelegramMenu_And_Login import  Menu_Telegram
        self.menu = Menu_Telegram(self.client)
        self.menu.show()
