from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QRadioButton,
    QVBoxLayout,
    QGroupBox,
    QButtonGroup,
    QLabel,
)
from PyQt5.QtGui import (
    QFont,
    QTextBlock,
    QTextDocument,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from plover_onscreen_stenotype.Main import Main
else:
    Main = object

from plover_onscreen_stenotype.settings import Settings, KeyLayout


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent: Main=None):
        super().__init__(parent)
        
        self.__settings = settings
    
        self.__setup_ui()

    def __setup_ui(self):
        self.setWindowTitle("On-screen stenotype settings")

        size = self.size()
        size.setWidth(350)
        self.resize(size)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setFont(QFont("Atkinson Hyperlegible", 11))


        radio_box = QGroupBox("Key layout", self)
        radio_group = QButtonGroup(radio_box)

        radios = {
            KeyLayout.STAGGERED: QRadioButton("Staggered", radio_box),
            KeyLayout.GRID: QRadioButton("Grid", radio_box),
        }
        radios[self.__settings.key_layout].setChecked(True)

        self.__key_layout_radios = {
            id(button): value
            for value, button in radios.items()
        }

        radio_box_layout = QVBoxLayout()
        for radio in radios.values():
            radio_box_layout.addWidget(radio)
            radio_group.addButton(radio)
        radio_box.setLayout(radio_box_layout)

        radio_group.buttonToggled.connect(self.__on_keyboard_layout_change)


        # sizes_box = QGroupBox(self)

        label_resizing = QLabel("Resize the stenotype window to adjust spacing", self)
        label_resizing.setWordWrap(True)
        label_resizing.setStyleSheet("font-style: italic; color: #7f000000;")

        label_troubleshooting = QLabel("If the window is unresponsive to many touches or touch input is delayed, check the plugin description (§ Recommended setup) for possible solutions",
                self)
        label_troubleshooting.setWordWrap(True)
        label_troubleshooting.setStyleSheet("font-style: italic; color: #7f000000;")


        layout = QVBoxLayout()
        layout.addWidget(radio_box)
        layout.addWidget(label_resizing)
        layout.addSpacing(8)
        layout.addWidget(label_troubleshooting)
        # layout.addWidget(sizes_box)
        self.setLayout(layout)


    def __on_keyboard_layout_change(self, button: QRadioButton, checked: bool):
        if not checked: return
        self.__settings.key_layout = self.__key_layout_radios[id(button)]
