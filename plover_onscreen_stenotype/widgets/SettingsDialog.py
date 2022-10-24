from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QRadioButton,
    QVBoxLayout,
    QGroupBox,
    QButtonGroup,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from plover_onscreen_stenotype.Main import Main
else:
    Main = object

from plover_onscreen_stenotype.settings import Settings, KeyboardLayout


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent: Main=None):
        super().__init__(parent)
        
        self.__settings = settings
    
        self.__setup_ui()

    def __setup_ui(self):
        self.setWindowTitle("On-screen stenotype settings")

        size = self.size()
        size.setWidth(175)
        self.resize(size)


        radio_box = QGroupBox("Key layout", self)
        radio_group = QButtonGroup(radio_box)

        radios = {
            KeyboardLayout.STAGGERED: QRadioButton("Staggered", radio_box),
            KeyboardLayout.GRID: QRadioButton("Straight", radio_box),
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


        layout = QVBoxLayout()
        layout.addWidget(radio_box)
        # layout.addWidget(sizes_box)
        self.setLayout(layout)


    def __on_keyboard_layout_change(self, button: QRadioButton, checked: bool):
        if not checked: return
        self.__settings.key_layout = self.__key_layout_radios[id(button)]
