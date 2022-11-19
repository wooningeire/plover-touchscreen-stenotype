from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QGroupBox,
    QButtonGroup,
    QRadioButton,
    QCheckBox,
    QSlider,
    QDoubleSpinBox,
    QLabel,
    QSizePolicy,
)
from PyQt5.QtGui import (
    QFont,
    QTextBlock,
    QTextDocument,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from plover_touchscreen_stenotype.Main import Main
else:
    Main = object

from plover_touchscreen_stenotype.settings import Settings, KeyLayout
from plover_touchscreen_stenotype.util import FONT_FAMILY


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent: Main=None):
        super().__init__(parent)
        
        self.__settings = settings
    
        self.__setup_ui()

    def __setup_ui(self):
        self.setWindowTitle("Touch stenotype settings")

        size = self.size()
        size.setWidth(350)
        self.resize(size)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.setFont(QFont(FONT_FAMILY, 11))


        key_layout_box = QGroupBox("Key layout", self)
        key_layout_group = QButtonGroup(key_layout_box)

        key_layout_radios = {
            KeyLayout.STAGGERED: QRadioButton("Staggered", key_layout_box),
            KeyLayout.GRID: QRadioButton("Grid", key_layout_box),
        }
        key_layout_radios[self.__settings.key_layout].setChecked(True)

        self.__key_layout_radios = {
            id(button): value
            for value, button in key_layout_radios.items()
        }

        key_layout_box_layout = QVBoxLayout()
        for radio in key_layout_radios.values():
            key_layout_box_layout.addWidget(radio)
            key_layout_group.addButton(radio)
        key_layout_box.setLayout(key_layout_box_layout)

        key_layout_group.buttonToggled.connect(self.__on_keyboard_layout_change)


        stroke_preview_box = QGroupBox("Stroke preview", self)

        stroke_preview_checkboxes = (
            QCheckBox("Show stroke", stroke_preview_box),
            QCheckBox("Show translation", stroke_preview_box),
        )
        stroke_preview_checkboxes[0].setChecked(self.__settings.stroke_preview_stroke)
        stroke_preview_checkboxes[1].setChecked(self.__settings.stroke_preview_translation)

        stroke_preview_box_layout = QVBoxLayout()
        for checkbox in stroke_preview_checkboxes:
            stroke_preview_box_layout.addWidget(checkbox)
        stroke_preview_box.setLayout(stroke_preview_box_layout)

        stroke_preview_checkboxes[0].toggled.connect(self.__on_stroke_preview_stroke_change)
        stroke_preview_checkboxes[1].toggled.connect(self.__on_stroke_preview_translation_change)


        size_box = QGroupBox("", self)

        # key_width_slider = QSlider(Qt.Horizontal, size_box)
        # key_width_slider.setMinimum(0.5)
        # key_width_slider.setMaximum(4)
        # key_width_slider.setSingleStep(0.1)
        # key_width_slider.setValue(self.__settings.key_width)

        # key_width_slider.valueChanged.connect(self.__on_key_width_change)

        key_width_box = QDoubleSpinBox(size_box)
        key_width_box.setMinimum(0.5)
        key_width_box.setMaximum(3)
        key_width_box.setSingleStep(0.1)
        key_width_box.setValue(self.__settings.key_width)
        
        key_width_box.valueChanged.connect(self.__on_key_width_change)


        label_resizing = QLabel("Resize the stenotype window to adjust spacing", self)
        label_resizing.setWordWrap(True)
        label_resizing.setStyleSheet("font-style: italic; color: #7f000000;")

        label_troubleshooting = QLabel("If there are issues with responsiveness, check the plugin description (§ Additional setup) for possible solutions",
                self)
        label_troubleshooting.setWordWrap(True)
        label_troubleshooting.setStyleSheet("font-style: italic; color: #7f000000;")


        layout = QVBoxLayout()
        layout.addWidget(key_layout_box)
        layout.addWidget(stroke_preview_box)
        layout.addWidget(size_box)
        layout.addWidget(label_resizing)
        layout.addSpacing(8)
        layout.addWidget(label_troubleshooting)
        # layout.addWidget(sizes_box)
        self.setLayout(layout)


    def __on_keyboard_layout_change(self, button: QRadioButton, checked: bool):
        if not checked: return
        self.__settings.key_layout = self.__key_layout_radios[id(button)]

    def __on_stroke_preview_stroke_change(self, checked: bool):
        self.__settings.stroke_preview_stroke = checked

    def __on_stroke_preview_translation_change(self, checked: bool):
        self.__settings.stroke_preview_translation = checked

    def __on_key_width_change(self, value: float):
        self.__settings.key_width = value
