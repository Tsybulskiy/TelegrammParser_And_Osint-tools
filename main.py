import sys

from PyQt5.QtWidgets import QApplication

from global_menu import Menu

if __name__ == "__main__":
    app = QApplication(sys.argv)

    menu_window = Menu()
    menu_window.show()

    sys.exit(app.exec())
