from PyQt5.QtWidgets import QMainWindow, QLineEdit, QListWidget, QPushButton, QVBoxLayout, QWidget, QMessageBox, \
    QFileDialog
import asyncio
from osint_functions import get_all_functions_from_modules, osint_func

class EmailOsint(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Email OSINT")
        self.setGeometry(100, 100, 200, 200)
        self.email_input = QLineEdit()
        self.start_button = QPushButton("Start")
        self.result_list = QListWidget()
        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        self.start_button.clicked.connect(self.start_osint)
        self.save_button = QPushButton("Сохранить в файл")
        self.save_button.clicked.connect(self.save_results)

        layout = QVBoxLayout()
        layout.addWidget(self.email_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.result_list)
        layout.addWidget(self.save_button)
        layout.addWidget(self.logout_button)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def start_osint(self):
        try:
            email = self.email_input.text()
            functions = get_all_functions_from_modules()
            asyncio.run(osint_func(email, functions, self.result_list))
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

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
