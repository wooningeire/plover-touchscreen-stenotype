from PyQt5.QtCore import (
    Qt,
    pyqtBoundSignal,
)
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QButtonGroup,
    QRadioButton,
    QCheckBox,
    QDoubleSpinBox,
    QLabel,
    QSizePolicy,
)
from PyQt5.QtGui import (
    QFont,
    QTextBlock,
    QTextDocument,
)

from typing import Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from ..Main import Main
else:
    Main = object

from .FloatInput import FloatSlider, FloatEntry
from ..settings import Settings, KeyLayout
from ..util import on, watch_many, FONT_FAMILY


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent: Main=None):
        super().__init__(parent)
        
        self.__settings = settings
    
        self.__setup_ui()

    def __setup_ui(self):
        self.setWindowTitle("Touch stenotype settings")

        size = self.size()
        size.setWidth(400)
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

        @on(key_layout_group.buttonToggled)
        def update_keyboard_layout(button: QRadioButton, checked: bool):
            if not checked: return
            self.__settings.key_layout = self.__key_layout_radios[id(button)]


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

        @on(stroke_preview_checkboxes[0].toggled)
        def update_stroke_preview_stroke(checked: bool):
            self.__settings.stroke_preview_stroke = checked

        @on(stroke_preview_checkboxes[1].toggled)
        def update_stroke_preview_translation(checked: bool):
            self.__settings.stroke_preview_translation = checked


        size_box = QGroupBox("Key and layout geometry", self)
        size_box_layout = QGridLayout()

        def update_key_width(value: float):
            self.__settings.key_width = value

        def update_key_height(value: float):
            self.__settings.key_height = value

        def update_compound_key_size(value: float):
            self.__settings.compound_key_size = value

        def update_index_stretch(value: float):
            self.__settings.index_stretch = value

        def update_pinky_stretch(value: float):
            self.__settings.pinky_stretch = value

        def update_vowel_set_offset(value: float):
            self.__settings.vowel_set_offset = value


        compound_key_box, compound_key_slider = _build_box_slider_pair(
            self.__settings.compound_key_size,
            update_compound_key_size,
            0.25,
            min(self.__settings.key_width, self.__settings.key_height),
            self.__settings.compound_key_size_change,
            parent=size_box,
        )

        @watch_many(self.__settings.key_width_change, self.__settings.key_height_change)
        def set_compound_key_size_max():
            new_max = min(self.__settings.key_width, self.__settings.key_height)

            compound_key_box.setMaximum(new_max)
            compound_key_slider.max = new_max


        for i, (label, box, slider, after_label) in enumerate((
            ("Base key width",
                *_build_box_slider_pair(
                    self.__settings.key_width,
                    update_key_width,
                    0.5,
                    3,
                    self.__settings.key_width_change,
                    parent=size_box,
                ), "cm"),
            ("Base key height",
                *_build_box_slider_pair(
                    self.__settings.key_height,
                    update_key_height,
                    0.5,
                    3,
                    self.__settings.key_height_change,
                    parent=size_box,
                ), "cm"),
            ("Compound key size", compound_key_box, compound_key_slider, "cm"),
            ("Index finger stretch",
                *_build_box_slider_pair(
                    self.__settings.index_stretch,
                    update_index_stretch,
                    0,
                    1,
                    self.__settings.index_stretch_change,
                    spin_box_step=0.05,
                    parent=size_box,
                ), "cm"),
            ("Pinky finger stretch",
                *_build_box_slider_pair(
                    self.__settings.pinky_stretch,
                    update_pinky_stretch,
                    0,
                    1.5,
                    self.__settings.pinky_stretch_change,
                    spin_box_step=0.05,
                    parent=size_box,
                ), "cm"),
            ("Vowels offset",
                *_build_box_slider_pair(
                    self.__settings.vowel_set_offset,
                    update_vowel_set_offset,
                    0,
                    1.5,
                    self.__settings.vowel_set_offset_change,
                    spin_box_step=0.1,
                    parent=size_box,
                ), "cm"),
        )):
            size_box_layout.addWidget(QLabel(label), i * 2, 0, 1, 3)
            size_box_layout.addWidget(slider, i * 2 + 1, 0)
            size_box_layout.addWidget(box, i * 2 + 1, 1)
            size_box_layout.addWidget(QLabel(after_label), i * 2 + 1, 2)
            
        size_box.setLayout(size_box_layout)


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



def _build_box_slider_pair(
    current_value: float,
    update_settings_attr: Callable[[float], None],
    min: float,
    max: float,
    settings_signal: pyqtBoundSignal,
    spin_box_step=0.1,
    parent: QWidget=None,
) -> tuple[FloatEntry, FloatSlider]:
    entry = FloatEntry(current_value, min=min, max=max, spin_step=spin_box_step, parent=parent)
    slider = FloatSlider(current_value, min=min, max=max, parent=parent)

    last_edit_from_entry = False
    last_edit_from_slider = False

    @on(entry.input)
    def on_entry_input(value: float):
        nonlocal last_edit_from_entry
        last_edit_from_entry = True
    @on(slider.input)
    def on_slider_input(value: float):
        nonlocal last_edit_from_slider
        last_edit_from_slider = True

    @on(entry.input)
    @on(slider.input)
    def update_settings(value: float):
        update_settings_attr(value)

    @on(settings_signal)
    def update_displays(value: float):
        nonlocal last_edit_from_entry
        nonlocal last_edit_from_slider

        # if not box.hasFocus():
        if not last_edit_from_entry:
            entry.current_value = value
        # if not slider.hasFocus():
        if not last_edit_from_slider:
            slider.current_value = value

        last_edit_from_entry = False
        last_edit_from_slider = False

    return entry, slider
