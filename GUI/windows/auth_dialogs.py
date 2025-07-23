from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setMinimumWidth(320)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Enter your credentials:")
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self._handle_login)
        layout.addWidget(self.label)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.btn_login)
        self.setLayout(layout)

    def _handle_login(self):
        # Mock JWT logic: accept any non-empty credentials
        if self.username.text() and self.password.text():
            QMessageBox.information(self, "Success", "Login successful! (mock JWT)")
            self.accept()
        else:
            QMessageBox.warning(
                self, "Error", "Please enter both username and password."
            )


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register")
        self.setMinimumWidth(320)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Create a new account:")
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.btn_register = QPushButton("Register")
        self.btn_register.clicked.connect(self._handle_register)
        layout.addWidget(self.label)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.btn_register)
        self.setLayout(layout)

    def _handle_register(self):
        # Mock registration logic: accept any non-empty credentials
        if self.username.text() and self.password.text():
            QMessageBox.information(
                self, "Success", "Registration successful! (mock JWT)"
            )
            self.accept()
        else:
            QMessageBox.warning(
                self, "Error", "Please enter both username and password."
            )


class LogoutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Logout")
        self.setMinimumWidth(260)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Are you sure you want to logout?")
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.clicked.connect(self.accept)
        layout.addWidget(self.label)
        layout.addWidget(self.btn_logout)
        self.setLayout(layout)
