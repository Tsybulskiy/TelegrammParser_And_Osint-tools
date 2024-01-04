import csv

import pytz
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QListWidget, QPushButton, QVBoxLayout, QFileDialog, QWidget, \
    QMessageBox
omsk_timezone = pytz.timezone('Asia/Omsk')


class TelegramChatParser(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_messages)
        self.dialog_dict = {}
        self.last_message_id = {}
        self.user_dict = {}
        self.setGeometry(100, 100, 500, 600)
        self.setWindowTitle("Telegram Chat Parser")
        self.label = QLabel("Название чата:", self)
        self.textbox = QLineEdit(self)
        self.label2 = QLabel("@username пользователя:", self)
        self.userbox = QLineEdit(self)
        self.start_button = QPushButton("Начать", self)
        self.start_button.clicked.connect(self.start_realtime_parsing)
        self.user_list = QListWidget(self)
        self.clear_button = QPushButton("Очистить", self)
        self.clear_button.clicked.connect(self.clear_user_list)
        self.stop_button = QPushButton("Остановить", self)
        self.stop_button.clicked.connect(self.stop_parsing)
        self.limit_label = QLabel("Введите количество сообщений для вывода", self)
        self.limit_input = QLineEdit(self)
        self.timer_label = QLabel("Введите интервал обновления в cс:", self)
        self.timer_input = QLineEdit(self)
        self.save_button = QPushButton("Сохранить сообщения в файл формата CSV", self)
        self.save_button.clicked.connect(self.save_to_csv)
        self.logout_button = QPushButton("Меню", self)
        self.logout_button.clicked.connect(self.logout)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.textbox)
        layout.addWidget(self.label2)
        layout.addWidget(self.userbox)
        layout.addWidget(self.limit_label)
        layout.addWidget(self.limit_input)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.timer_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.user_list)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.logout_button)
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def save_to_csv(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
            if filename:

                with open(filename, 'w', newline='', encoding='utf-16') as file:
                    writer = csv.writer(file, delimiter=',')
                    writer.writerow(["User", "Message", "Chat", "Date"])
                    for row in range(self.user_list.count()):
                        item = self.user_list.item(row)
                        values = item.text().split(" - ")
                        writer.writerow(values)

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def stop_parsing(self):
        if self.timer.isActive():
            self.timer.stop()
        self.dialog_dict.clear()
        self.user_dict.clear()

    def clear_user_list(self):
        self.user_list.clear()

    def start_realtime_parsing(self):
        try:
            chats = self.textbox.text().split(",")
            users = self.userbox.text().split(",")
            dialogs = self.client.get_dialogs()

            for dialog in dialogs:
                if dialog.title in chats:
                    chat_id = int(dialog.id)
                    self.dialog_dict[chat_id] = dialog.title
                    self.last_message_id[chat_id] = {user: 0 for user in users}
            interval_seconds = int(self.timer_input.text())
            interval_ms = interval_seconds * 1000
            self.timer.start(interval_ms)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def display_messages(self):
        try:
            chat_ids = list(self.dialog_dict.keys())
            users = self.userbox.text().split(",")
            limit = int(self.limit_input.text())

            for user in users:
                for chat_id in chat_ids:
                    chat_name = self.dialog_dict[chat_id]
                    last_message_id = self.last_message_id[chat_id].get(user, 0)
                    messages_from_user = []
                    for message in self.client.iter_messages(chat_id, from_user=user, min_id=last_message_id,
                                                             limit=limit):
                        self.user_list.addItem(
                            f" {user} Message: {message.text} - Chat: {chat_name} - Date: {message.date.astimezone(omsk_timezone)}")
                        messages_from_user.append(message)
                        if message.id > last_message_id:
                            last_message_id = message.id
                    self.last_message_id[chat_id][user] = last_message_id
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

