import os
import threading

import netifaces
import pyshark
import requests
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QWidget, QComboBox, QLabel, QPushButton, QListView, QMessageBox, QVBoxLayout


class PacketSniffer(QWidget):
    def __init__(self, client):
        super().__init__()
        self.kill_timer = None
        self.client = client
        self.ips = set()
        self.interfaces = netifaces.interfaces()
        self.interface_label = QLabel("Интерфейс:")
        self.interface_combobox = QComboBox(self)
        for iface in self.interfaces:
            ip_addresses = netifaces.ifaddresses(iface).get(netifaces.AF_INET)
            ip_address = ip_addresses[0]['addr'] if ip_addresses else "Нет ip-адреса"
            self.interface_combobox.addItem(f"{iface} ({ip_address})")

        self.start_button = QPushButton("Начать захват")
        self.start_button.clicked.connect(self.start_sniffing)

        self.list_view = QListView()
        self.list_model = QStringListModel()
        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        layout = QVBoxLayout()
        layout.addWidget(self.interface_label)
        layout.addWidget(self.interface_combobox)
        layout.addWidget(self.start_button)
        layout.addWidget(self.list_view)
        layout.addWidget(self.logout_button)
        self.setLayout(layout)
        self.setWindowTitle("Packet Sniffer")

    def start_sniffing(self):
        try:
            selected_interface_text = self.interface_combobox.currentText()
            selected_interface = selected_interface_text.split(" ")[0]

            interface = "\\Device\\NPF_" + selected_interface

            capture = pyshark.LiveCapture(interface=interface, display_filter='stun')

            for packet in capture.sniff_continuously():

                if packet.stun:
                    xor_mapped_address = packet.stun.get_field_value('stun.att.ipv4')
                    if xor_mapped_address and xor_mapped_address not in self.ips:
                        if self.kill_timer is not None:
                            self.kill_timer.cancel()
                        self.kill_timer = threading.Timer(15.0, self.kill_processes)
                        self.kill_timer.start()
                        try:
                            response = requests.get(f"http://ip-api.com/json/{xor_mapped_address}")
                            data = response.json()
                            self.show_info(xor_mapped_address, data)
                            self.ips.add(xor_mapped_address)
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

    def kill_processes(self):
        os.system("taskkill /f /im tshark.exe /t")
        os.system("taskkill /f /im dumpcap.exe /t")

    def show_info(self, xor_mapped_address, data):
        try:
            info = f" Найден IP Адрес: {xor_mapped_address} - Страна: {data.get('country', 'N/A')} - Код страны: {data.get('countryCode', 'N/A')} - Код региона: {data.get('region', 'N/A')} - Название региона: {data.get('regionName', 'N/A')} -  Город: {data.get('city', 'N/A')} -  Индекс: {data.get('zip', 'N/A')} - Широта: {data.get('lat', 'N/A')} - Долгота: {data.get('lon', 'N/A')} - Временная зона: {data.get('timezone', 'N/A')} - Провайдер: {data.get('isp', 'N/A')} - Организация: {data.get('org', 'N/A')} - Автономная система: {data.get('as', 'N/A')}"

            self.list_model.insertRow(0)
            self.list_model.setData(self.list_model.index(0), info)
            self.list_view.setModel(self.list_model)

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(f"Ошибка: {str(e)}")
            msg.exec_()

    def logout(self):
        self.close()
        from TelegramMenu_And_Login import Menu_Telegram
        self.menu = Menu_Telegram(self.client)
        self.menu.show()