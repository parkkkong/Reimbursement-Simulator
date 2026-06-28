from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtUiTools import QUiLoader
from pathlib import Path


class DesignerMainWindow(QtWidgets.QMainWindow):
    def __init__(self, ui_path: str | None = None) -> None:
        super().__init__()
        ui_file = Path(ui_path or Path(__file__).with_name("main_window.ui"))
        loader = QUiLoader()
        self.ui = loader.load(str(ui_file), self)
        if self.ui is None:
            raise RuntimeError(f"Failed to load UI file: {ui_file}")

        self.setCentralWidget(self.ui)
