from PyQt5.QtCore import (
    Qt,
    pyqtBoundSignal,
)
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QButtonGroup,
    QRadioButton,
    QCheckBox,
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


        settings = self.__settings


        key_layout_box = QGroupBox("Key layout", self)
        key_layout_group = QButtonGroup(key_layout_box)

        key_layout_radios = {
            KeyLayout.STAGGERED: QRadioButton("Staggered", key_layout_box),
            KeyLayout.GRID: QRadioButton("Grid", key_layout_box),
        }
        key_layout_radios[settings.key_layout].setChecked(True)

        self.__key_layout_radios = {
            id(button): value
            for value, button in key_layout_radios.items()
        }

        key_layout_box_layout = QVBoxLayout()
        for radio in key_layout_radios.values():
            key_layout_box_layout.addWidget(radio)
            key_layout_group.addButton(radio)

        key_layout_box_layout.addStretch(1)
        key_layout_box.setLayout(key_layout_box_layout)

        @on(key_layout_group.buttonToggled)
        def update_keyboard_layout(button: QRadioButton, checked: bool):
            if not checked: return
            settings.key_layout = self.__key_layout_radios[id(button)]


        stroke_preview_box = QGroupBox("Stroke preview", self)

        stroke_preview_checkboxes = (
            QCheckBox("Show stroke", stroke_preview_box),
            QCheckBox("Show translation", stroke_preview_box),
        )
        stroke_preview_checkboxes[0].setChecked(settings.stroke_preview_stroke)
        stroke_preview_checkboxes[1].setChecked(settings.stroke_preview_translation)

        stroke_preview_box_layout = QVBoxLayout()
        for checkbox in stroke_preview_checkboxes:
            stroke_preview_box_layout.addWidget(checkbox)
            
        stroke_preview_box_layout.addStretch(1)
        stroke_preview_box.setLayout(stroke_preview_box_layout)

        @on(stroke_preview_checkboxes[0].toggled)
        def update_stroke_preview_stroke(checked: bool):
            settings.stroke_preview_stroke = checked

        @on(stroke_preview_checkboxes[1].toggled)
        def update_stroke_preview_translation(checked: bool):
            settings.stroke_preview_translation = checked


        size_box = QGroupBox("Key and layout geometry", self)
        size_box_layout = QGridLayout()

        def update_key_width(value: float):
            settings.key_width = value

        def update_key_height(value: float):
            settings.key_height = value

        def update_compound_key_size(value: float):
            settings.compound_key_size = value

        def update_index_stretch(value: float):
            settings.index_stretch = value

        def update_pinky_stretch(value: float):
            settings.pinky_stretch = value

        def update_vowel_set_offset(value: float):
            settings.vowel_set_offset = value

        def update_index_stagger_fac(value: float):
            settings.index_stagger_fac = value

        def update_middle_stagger_fac(value: float):
            settings.middle_stagger_fac = value

        def update_ring_stagger_fac(value: float):
            settings.ring_stagger_fac = value

        def update_pinky_stagger_fac(value: float):
            settings.pinky_stagger_fac = value


        compound_key_box, compound_key_slider = _build_entry_slider_pair(
            settings.compound_key_size,
            update_compound_key_size,
            settings.compound_key_size_change,
            min=0.25,
            max=min(settings.key_width, settings.key_height),
            parent=size_box,
        )

        @watch_many(settings.key_width_change, settings.key_height_change)
        def set_compound_key_size_max():
            new_max = min(settings.key_width, settings.key_height)

            compound_key_box.setMaximum(new_max)
            compound_key_slider.max = new_max


        for size_box_index, (label, box, slider, after_label) in enumerate((
            ("Base key width",
                *_build_entry_slider_pair(
                    settings.key_width,
                    update_key_width,
                    settings.key_width_change,
                    min=0.5,
                    max=3,
                    parent=size_box,
                ), "cm"),
            ("Base key height",
                *_build_entry_slider_pair(
                    settings.key_height,
                    update_key_height,
                    settings.key_height_change,
                    min=0.5,
                    max=3,
                    parent=size_box,
                ), "cm"),
            ("Compound key size", compound_key_box, compound_key_slider, "cm"),
            ("Index finger stretch",
                *_build_entry_slider_pair(
                    settings.index_stretch,
                    update_index_stretch,
                    settings.index_stretch_change,
                    min=0,
                    max=1,
                    spin_box_step=0.05,
                    parent=size_box,
                ), "cm"),
            ("Pinky finger stretch",
                *_build_entry_slider_pair(
                    settings.pinky_stretch,
                    update_pinky_stretch,
                    settings.pinky_stretch_change,
                    min=0,
                    max=1.5,
                    spin_box_step=0.05,
                    parent=size_box,
                ), "cm"),
            ("Vowels offset",
                *_build_entry_slider_pair(
                    settings.vowel_set_offset,
                    update_vowel_set_offset,
                    settings.vowel_set_offset_change,
                    min=0,
                    max=1.5,
                    spin_box_step=0.1,
                    parent=size_box,
                ), "cm"),
        )):
            size_box_layout.addWidget(QLabel(label), size_box_index * 2, 0, 1, 3)
            size_box_layout.addWidget(slider, size_box_index * 2 + 1, 0)
            size_box_layout.addWidget(box, size_box_index * 2 + 1, 1)
            size_box_layout.addWidget(QLabel(after_label), size_box_index * 2 + 1, 2)

        size_box_index += 1

        size_box_layout.addWidget(QLabel("Column stagger factors"), size_box_index * 2, 0, 1, 3)

        stagger_layout = QGridLayout()
        stagger_layout.setContentsMargins(0, 0, 0, 0)
        stagger_layout.setRowMinimumHeight(0, 120)
        for stagger_index, (value, callback, signal) in enumerate((
            (settings.index_stagger_fac, update_index_stagger_fac, settings.index_stagger_fac_change),
            (settings.middle_stagger_fac, update_middle_stagger_fac, settings.middle_stagger_fac_change),
            (settings.ring_stagger_fac, update_ring_stagger_fac, settings.ring_stagger_fac_change),
            (settings.pinky_stagger_fac, update_pinky_stagger_fac, settings.pinky_stagger_fac_change),
        )):
            entry, slider = _build_entry_slider_pair(
                value,
                callback,
                signal,
                min=0,
                max=1,
                spin_box_step=0.05,
                slider_orientation=Qt.Vertical,
                parent=size_box,
            )

            stagger_layout.addWidget(slider, 0, stagger_index, Qt.AlignHCenter)
            stagger_layout.addWidget(entry, 1, stagger_index, Qt.AlignHCenter)

        size_box_layout.addLayout(stagger_layout, size_box_index * 2 + 1, 0, 1, 3)
        
        # size_box_layout.setRowStretch(2 * (size_box_index + 1), 1)
        size_box.setLayout(size_box_layout)


        label_resizing = QLabel("Resize the stenotype window to adjust spacing", self)
        label_resizing.setWordWrap(True)
        label_resizing.setStyleSheet("font-style: italic; color: #7f000000;")

        label_troubleshooting = QLabel("If there are issues with responsiveness, check the plugin description (§ Additional setup) for possible solutions",
                self)
        label_troubleshooting.setWordWrap(True)
        label_troubleshooting.setStyleSheet("font-style: italic; color: #7f000000;")


        layout = QGridLayout()
        layout.addWidget(key_layout_box, 0, 0)
        layout.addWidget(stroke_preview_box, 1, 0)
        layout.addWidget(size_box, 0, 1, 3, 1)
        layout.setRowStretch(2, 1)
        layout.addWidget(label_resizing, 3, 0, 1, 2)
        layout.addWidget(label_troubleshooting, 4, 0, 1, 2)
        # layout.addWidget(sizes_box)
        self.setLayout(layout)



def _build_entry_slider_pair(
    current_value: float,
    update_settings_attr: Callable[[float], None],
    settings_signal: pyqtBoundSignal,
    min: float=0,
    max: float=1,
    spin_box_step=0.1,
    slider_orientation: Qt.Orientation=Qt.Horizontal,
    parent: QWidget=None,
) -> tuple[FloatEntry, FloatSlider]:
    entry = FloatEntry(current_value,
            min=min,
            max=max,
            spin_step=spin_box_step,
            parent=parent)
    slider = FloatSlider(current_value,
            min=min,
            max=max,
            orientation=slider_orientation,
            parent=parent)

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
