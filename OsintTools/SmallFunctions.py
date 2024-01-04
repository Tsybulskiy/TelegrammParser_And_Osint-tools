import requests
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton, QListWidget, QVBoxLayout, QWidget, QMessageBox, \
    QFileDialog
from ipwhois import IPWhois


class SmallFunctions(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Мелкие Функции")
        self.setGeometry(100, 100, 200, 200)
        self.ip_input = QLineEdit()
        self.start_button = QPushButton("Получить информацию о IP-Адресе")
        self.number_input = QLineEdit()
        self.start2_button = QPushButton("Получить информацию о номере телефона")
        self.result_list = QListWidget()
        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        self.start_button.clicked.connect(self.get_ip_info)
        self.start2_button.clicked.connect(self.get_number_info)
        self.save_button = QPushButton("Сохранить в файл")
        self.save_button.clicked.connect(self.save_results)
        layout = QVBoxLayout()
        layout.addWidget(self.ip_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.number_input)
        layout.addWidget(self.start2_button)
        layout.addWidget(self.result_list)
        layout.addWidget(self.save_button)
        layout.addWidget(self.logout_button)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def get_number_info(self):
        number = self.number_input.text()
        clear_phone_number = "".join([i for i in number if i.isdigit()])
        api_key = "80fd4720becad81c5d60f5364c7d4b2f"
        url = "http://apilayer.net/api/validate"
        try:
            response = requests.get(
                url,
                params={"access_key": api_key, "number": clear_phone_number}
            )

            result = response.json()
            self.result_list.clear()
            if not result["valid"]:
                self.result_list.addItem("Ошибка: неверный номер мобильного телефона")
            else:
                self.result_list.addItem(f"Сам номер: {result['number']}")
                self.result_list.addItem(f" Тип: {result['line_type']}")
                self.result_list.addItem(f"Код страны: {result['country_code']}")
                self.result_list.addItem(f"Страна: {result['country_name']}")
                self.result_list.addItem(f"Геолокация: {result['location']}")
                self.result_list.addItem(f"Оператор: {result['carrier']}")
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def get_ip_info(self):
        try:
            self.result_list.clear()
            ip = self.ip_input.text()
            whois = IPWhois(ip)
            result = whois.lookup_whois()

            self.print_to_list(result)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def print_to_list(self, data, indent=""):
        for key, value in data.items():
            if isinstance(value, dict):
                self.result_list.addItem(f"{indent}{key}:")
                self.print_to_list(value, indent + "\t")
            elif isinstance(value, list):
                self.result_list.addItem(f"{indent}{key}:")
                for item in value:
                    self.print_to_list(item, indent + "\t")
            else:
                self.result_list.addItem(f"{indent}{key}: {value}")

    def save_results(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, 'Сохранить результаты', '', 'Text Files (*.txt)')
            if file_path:
                with open(file_path, "w") as f:
                    for i in range(self.result_list.count()):
                        f.write(self.result_list.item(i).text() + "\n")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Результаты успешно сохранены в файл!")
                msg.exec_()
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