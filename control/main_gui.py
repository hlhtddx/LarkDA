import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from ui.main import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionLogin.triggered.connect(self.on_login_clicked)
        self.ui.actionLogOut.triggered.connect(self.on_logout_clicked)

    def on_set_workspace_clicked(self):
        pass

    def on_login_clicked(self):
        self.ui.actionLogOut.setVisible(True)
        self.ui.actionLogin.setVisible(False)

    def on_logout_clicked(self):
        self.ui.actionLogOut.setVisible(False)
        self.ui.actionLogin.setVisible(True)


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
