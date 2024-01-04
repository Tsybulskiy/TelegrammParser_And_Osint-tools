import datetime

import dns
import requests
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QListWidget, QAbstractItemView, QWidget, \
    QVBoxLayout, QMessageBox


class Search_Domain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.headers = {'accept': 'application/json', }
        self.setGeometry(100, 100, 200, 200)
        self.setWindowTitle(" Search Domain")
        self.label3 = QLabel(
            "Количество дней для получение записей или 0 если нужны все действительные, или -1 если нужны все даже недействительные",
            self)
        self.daybox = QLineEdit(self)
        self.label = QLabel("Домен:", self)
        self.domenbox = QLineEdit(self)
        self.search_button = QPushButton("Получить Сабдомены")
        self.search_button.clicked.connect(self.search_subdommens)
        self.record_button = QPushButton("Получить Записи DNS")
        self.record_button.clicked.connect(self.get_record)
        self.result_list = QListWidget(self)
        self.label2 = QLabel("Часть домена (не менее 5 символов для поиска доменов с части домена):", self)
        self.partbox = QLineEdit(self)
        self.button_domen = QPushButton("Найти все домены с части домена")
        self.button_domen.clicked.connect(self.search_domen)
        self.button_tld = QPushButton("Найти все домены третьего уровня")
        self.button_tld.clicked.connect(self.search_tld)
        self.result_list2 = QListWidget(self)
        self.result_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.result_list2.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        layout = QVBoxLayout()
        layout.addWidget(self.label3)
        layout.addWidget(self.daybox)
        layout.addWidget(self.label)
        layout.addWidget(self.domenbox)
        layout.addWidget(self.search_button)
        layout.addWidget(self.record_button)
        layout.addWidget(self.result_list)
        layout.addWidget(self.label2)
        layout.addWidget(self.partbox)
        layout.addWidget(self.button_domen)
        layout.addWidget(self.button_tld)
        layout.addWidget(self.result_list2)
        layout.addWidget(self.logout_button)
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def search_subdommens(self):
        self.result_list.clear()
        try:
            headers = self.headers
            days = self.daybox.text()
            domain = self.domenbox.text()
            params = {'days': f'{days}', }
            response_subdommens = requests.get(f'https://columbus.elmasy.com/api/lookup/{domain}', params=params,
                                               headers=headers)
            for i in range(len(response_subdommens.json())):
                if response_subdommens.json()[i] != '':
                    subdomain = response_subdommens.json()[i]
                    info = f'{subdomain}/{domain}'
                    self.result_list.addItem(info)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def get_record(self):
        self.result_list.clear()
        try:
            headers = self.headers
            days = self.daybox.text()
            domain = self.domenbox.text()
            params = {'days': f'{days}', }
            response_history = requests.get(f'https://columbus.elmasy.com/api/history/{domain}', params=params,
                                            headers=self.headers)
            records_list = []
            for item in response_history.json():
                for record in item['Records']:
                    tip = dns.rdatatype.to_text(record['type'])
                    value = record['value']
                    time = record['time']
                    dt_object = datetime.datetime.fromtimestamp(time)
                    time = dt_object.strftime("%d-%m-%Y")
                    records_list.append({'tip': tip, 'value': value, 'time': time})
            sorted_records = sorted(records_list, key=lambda k: k['time'], reverse=True)
            for record in sorted_records:
                record_text = f"Тип Записи: {record['tip']}, DNS Запись: {record['value']}, Дата Записи: {record['time']}"
                self.result_list.addItem(record_text)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def search_domen(self):
        self.result_list2.clear()
        try:
            headers = self.headers
            domain = self.partbox.text()
            response_domains = requests.get(f'https://columbus.elmasy.com/api/starts/{domain}', headers=headers)
            for i in range(len(response_domains.json())):
                if response_domains.json()[i] != '':
                    domain = response_domains.json()[i]
                    info = f'{domain}'
                    self.result_list2.addItem(info)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def search_tld(self):
        self.result_list2.clear()
        try:
            headers = self.headers
            domain = self.partbox.text()
            response_tld = requests.get(f'https://columbus.elmasy.com/api/tld/{domain}', headers=headers)
            for i in range(len(response_tld.json())):
                if response_tld.json()[i] != '':
                    tld = response_tld.json()[i]
                    info = f'{domain}.{tld}'
                    self.result_list2.addItem(info)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def logout(self):
        self.close()
        from osint import Menu_Osint
        self.menu = Menu_Osint()
        self.menu.show()