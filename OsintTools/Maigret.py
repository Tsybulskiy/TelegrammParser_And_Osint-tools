import asyncio
import logging

import maigret
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QWidget, QMessageBox
from maigret.report import save_html_report, save_pdf_report, save_xmind_report, generate_report_context

class Maigret(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 200, 200)
        self.setWindowTitle("Small Functions")

        self.label = QLabel("@username пользователя:", self)
        self.userbox = QLineEdit(self)

        self.maigret_button = QPushButton("Получить другие аккаунты пользователя (PDF,HTML)")
        self.maigret_button.clicked.connect(self.maigret_parse)

        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)

        self.pdf_checkbox = QCheckBox("PDF")
        self.html_checkbox = QCheckBox("HTML")
        self.xmind_checkbox = QCheckBox("XMind")

        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(self.userbox)

        layout.addWidget(self.maigret_button)
        layout.addWidget(self.pdf_checkbox)
        layout.addWidget(self.html_checkbox)
        layout.addWidget(self.xmind_checkbox)
        layout.addWidget(self.logout_button)

        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def logout(self):
        self.close()
        from osint import Menu_Osint
        self.menu = Menu_Osint()
        self.menu.show()

    def maigret_parse(self):
        try:
            TIMEOUT = 10
            MAX_CONNECTIONS = 50
            id_type = "username"
            logger = logging.getLogger()
            logger.setLevel(logging.CRITICAL)
            loop = asyncio.get_event_loop()

            db = maigret.MaigretDatabase().load_from_file('data.json')

            username = self.userbox.text()
            sites_count = len(db.sites_dict)
            sites = db.ranked_sites_dict(top=sites_count)

            selected_reports = []
            if self.pdf_checkbox.isChecked():
                selected_reports.append("PDF")
            if self.html_checkbox.isChecked():
                selected_reports.append("HTML")
            if self.xmind_checkbox.isChecked():
                selected_reports.append("XMind")

            if not selected_reports:
                QMessageBox.critical(self, "Ошибка", "Выберите хотя бы один отчет")
                return

            search_func = maigret.search(
                username=username,
                site_dict=sites,
                timeout=TIMEOUT,
                logger=logger,
                max_connections=MAX_CONNECTIONS,
                html_report="HTML" in selected_reports,
                pdf_report="PDF" in selected_reports,
                xmind_report="XMind" in selected_reports,
                id_type=id_type,
                no_progressbar='n',
            )

            results = loop.run_until_complete(search_func)
            general_results = []
            general_results.append((username, id_type, results))
            report_context = generate_report_context(general_results)

            for report_type in selected_reports:
                if report_type == "PDF":
                    save_pdf_report(f"{username}_report.pdf", report_context)
                elif report_type == "HTML":
                    save_html_report(f"{username}_report.html", report_context)
                elif report_type == "XMind":
                    save_xmind_report(f"{username}_reportx.xmind", username, results)

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()
