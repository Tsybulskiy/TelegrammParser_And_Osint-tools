from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox

from EmailOsint import EmailOsint
from PhotoOsint import PhotoOsint
from SearchDomain import Search_Domain
from SmallFunctions import SmallFunctions
from Maigret import Maigret

class Menu_Osint(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu_Osint")
        self.setGeometry(100, 100, 200, 200)

        layout = QVBoxLayout()
        self.maigret_button = QPushButton("Получение других акккаунтов пользователя по username")
        self.maigret_button.clicked.connect(self.open_maigret)
        self.dns_button = QPushButton("DNS Osint")
        self.dns_button.clicked.connect(self.open_dns)
        self.photoosint_button = QPushButton("Photo Osint")
        self.photoosint_button.clicked.connect(self.open_photoosint)
        self.email_button = QPushButton("Email Checker")
        self.email_button.clicked.connect(self.open_email)
        self.smallfunctions_button = QPushButton("Маленькие Функции")
        self.smallfunctions_button.clicked.connect(self.open_smallfunctions)
        self.logout_button = QPushButton("Выход")
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.maigret_button)
        layout.addWidget(self.dns_button)
        layout.addWidget(self.photoosint_button)
        layout.addWidget(self.email_button)
        layout.addWidget(self.smallfunctions_button)
        layout.addWidget(self.logout_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_maigret(self):
        try:
            self.maigret_window = Maigret()
            self.maigret_window.show()
            self.close()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def open_dns(self):
        try:
            self.dns_window = Search_Domain()
            self.dns_window.show()
            self.close()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()
    def open_photoosint(self):
        try:
            self.photoosint_window = PhotoOsint()
            self.photoosint_window.show()
            self.close()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def open_email(self):
        try:
            self.email_window = EmailOsint()
            self.email_window.show()
            self.close()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def open_smallfunctions(self):
        try:
            self.smallfunctions_window = SmallFunctions()
            self.smallfunctions_window.show()
            self.close()
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def logout(self):
        self.close()
        from global_menu import Menu
        self.menu = Menu()
        self.menu.show()