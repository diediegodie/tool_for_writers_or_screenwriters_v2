from PySide6.QtWidgets import QApplication, QWidget
from GUI.windows.homepage import HomepageWindow
import sys


def main():
    app = QApplication(sys.argv)
    window = HomepageWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
