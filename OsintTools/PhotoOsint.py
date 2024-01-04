import requests
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QLabel, QPushButton, QListWidget, QVBoxLayout, QWidget, QMessageBox, \
    QFileDialog, QAbstractItemView
from google_img_source_search import ReverseImageSearcher

class PhotoOsint(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = '7a1d185f82f20f5'
        self.setGeometry(100, 100, 200, 200)
        self.setWindowTitle("Search Domain")
        self.headers = {'Authorization': 'Client-ID ' + self.api_key}
        self.label = QLabel("Введите количество записей для вывода")
        self.record_box = QLineEdit(self)
        self.label2 = QLabel("Введите ссылку на картинку или нажмить Получить результаты если хотите загрузить её")
        self.url_box = QLineEdit(self)
        self.start_button = QPushButton("Получить результаты")
        self.save_button = QPushButton("Сохранить в файл")
        self.start_button.clicked.connect(self.get_results)
        self.save_button.clicked.connect(self.save_results)
        self.result_list = QListWidget(self)
        self.result_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.record_box)
        layout.addWidget(self.label2)
        layout.addWidget(self.url_box)
        layout.addWidget(self.start_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.result_list)
        layout.addWidget(self.logout_button)
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def get_results(self):
        self.result_list.clear()
        try:
            records = self.record_box.text()
            if not records:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка: введите количество записей")
                msg.exec_()
                return

            url_input = self.url_box.text()
            if url_input:
                self.search_image(url_input, int(records))
            else:
                file_path = ""
                dialog = QFileDialog()
                dialog.setFileMode(QFileDialog.AnyFile)
                dialog.setViewMode(QFileDialog.Detail)
                if dialog.exec_():
                    file_path = dialog.selectedFiles()[0]
                    if file_path:
                        self.upload_file_to_imgur(file_path)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def upload_file_to_imgur(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            headers = {'Authorization': 'Client-ID ' + self.api_key}
            form = {'image': file_data}
            response = requests.post('https://api.imgur.com/3/image', headers=headers, files=form)
            json_data = response.json()
            image_url = json_data['data']['link']
            self.search_image(image_url, int(self.record_box.text()))
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def search_image(self, image_url, num_results):
        try:
            rev_img_searcher = ReverseImageSearcher()
            res = rev_img_searcher.search(image_url)
            for i, search_item in enumerate(res[:num_results]):
                result_text = f'Result {i + 1}:\n'
                result_text += f'Title: {search_item.page_title}\n'
                result_text += f'Site: {search_item.page_url}\n'
                result_text += f'Img: {search_item.image_url}\n'
                self.result_list.addItem(result_text)
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