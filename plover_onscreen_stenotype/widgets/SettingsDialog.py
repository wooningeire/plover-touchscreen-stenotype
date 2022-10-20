from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QRadioButton,
    QVBoxLayout,
    QGroupBox,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from plover_onscreen_stenotype.Main import Main
else:
    Main = object


class SettingsDialog(QDialog):
    def __init__(self, parent: Main=None):
        super().__init__(parent)
    
        self.__setup_ui()

    def __setup_ui(self):
        self.setWindowTitle("On-screen stenotype settings")


        radio_box = QGroupBox("Key layout", self)

        radios = (
            QRadioButton("Staggered", radio_box),
            QRadioButton("Straight", radio_box),
        )
        radios[0].setChecked(True)

        radio_box_layout = QVBoxLayout()
        for radio in radios:
            radio_box_layout.addWidget(radio)
        radio_box.setLayout(radio_box_layout)

        
        sizes_box = QGroupBox("Dimensions", self)
            

        layout = QVBoxLayout()
        layout.addWidget(radio_box)
        layout.addWidget(sizes_box)
        self.setLayout(layout)
