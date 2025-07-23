from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt
from GUI.windows.auth_dialogs import LoginDialog, RegisterDialog, LogoutDialog
from GUI.windows.dashboard import DashboardWindow


class HomepageWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Writer & Screenwriter Assistant")
        self.setMinimumSize(500, 350)
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Welcome to Writer & Screenwriter Assistant")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 20px;")

        subtitle = QLabel("Your creative writing workspace.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #666;")

        btn_login = QPushButton("Login")
        btn_register = QPushButton("Register")
        btn_logout = QPushButton("Logout")
        btn_dashboard = QPushButton("Open Dashboard")
        for btn in (btn_login, btn_register, btn_logout, btn_dashboard):
            btn.setMinimumWidth(180)
            btn.setStyleSheet("font-size: 15px; margin: 8px 0;")

        btn_login.clicked.connect(self.open_login_dialog)
        btn_register.clicked.connect(self.open_register_dialog)
        btn_logout.clicked.connect(self.open_logout_dialog)
        btn_dashboard.clicked.connect(self.open_dashboard_window)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(btn_login)
        layout.addWidget(btn_register)
        layout.addWidget(btn_logout)
        layout.addWidget(btn_dashboard)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_dashboard_window(self):
        self.dashboard = DashboardWindow(self)
        self.dashboard.show()

    def open_login_dialog(self):
        dialog = LoginDialog(self)
        dialog.exec()

    def open_register_dialog(self):
        dialog = RegisterDialog(self)
        dialog.exec()

    def open_logout_dialog(self):
        dialog = LogoutDialog(self)
        dialog.exec()
