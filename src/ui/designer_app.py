"""Main application entry point for the Designer."""

import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import DesignerMainWindow


def main():
    """Run the Designer application."""
    app = QApplication(sys.argv)
    
    window = DesignerMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

