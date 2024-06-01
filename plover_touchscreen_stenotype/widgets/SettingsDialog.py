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
from ..lib.reactivity import Ref, on, watch_many
from ..lib.constants import FONT_FAMILY


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


        window_box = QGroupBox("Window", self)
        window_box_layout = QGridLayout()

        opacity_entry, opacity_slider = _build_entry_slider_pair(
            settings.window_opacity_ref,
            min=0.25,
            max=1,
            parent=window_box,
        )

        frameless_checkbox = QCheckBox("Frameless (need to reopen window)", window_box)
        frameless_checkbox.setChecked(settings.frameless)
        @on(frameless_checkbox.toggled)
        def update_frameless(checked: bool):
            settings.frameless = checked
        
        window_box_layout.addWidget(QLabel("Opacity"), 0, 0, 1, 3)
        window_box_layout.addWidget(opacity_slider, 1, 0)
        window_box_layout.addWidget(opacity_entry, 1, 1)

        for window_box_index, (label, box, slider, after_label) in enumerate((
            ("Width",
                *_build_entry_slider_pair(
                    settings.window_width_ref,
                    min=20,
                    max=50,
                    spin_box_step=0.5,
                    parent=window_box,
                ), "cm"),
            ("Height",
                *_build_entry_slider_pair(
                    settings.window_height_ref,
                    min=8,
                    max=20,
                    spin_box_step=0.5,
                    parent=window_box,
                ), "cm"),
        )):
            window_box_layout.addWidget(QLabel(label), window_box_index * 2 + 2, 0, 1, 3)
            window_box_layout.addWidget(slider, window_box_index * 2 + 3, 0)
            window_box_layout.addWidget(box, window_box_index * 2 + 3, 1)
            window_box_layout.addWidget(QLabel(after_label), window_box_index * 2 + 3, 2)

        window_box_layout.addWidget(frameless_checkbox, 6, 0, 1, 3)

        window_box.setLayout(window_box_layout)



        size_box = QGroupBox("Key and layout geometry", self)
        size_box_layout = QGridLayout()

        for window_box_index, (label, box, slider, after_label) in enumerate((
            ("Base key width",
                *_build_entry_slider_pair(
                    settings.key_width_ref,
                    min=0.5,
                    max=3,
                    spin_box_step=0.05,
                    parent=size_box,
                ), "cm"),
            ("Base key height",
                *_build_entry_slider_pair(
                    settings.key_height_ref,
                    min=0.5,
                    max=3,
                    spin_box_step=0.05,
                    parent=size_box,
                ), "cm"),
            ("Compound key size",
                    *(compound_input_pair := _build_entry_slider_pair(
                        settings.compound_key_size_ref,
                        min=0.25,
                        max=min(settings.key_width, settings.key_height),
                        spin_box_step=0.05,
                        parent=size_box,
                    )), "cm"),
            ("Index finger stretch",
                *_build_entry_slider_pair(
                    settings.index_stretch_ref,
                    min=-0.25,
                    max=1,
                    spin_box_step=0.05,
                    parent=size_box,
                ), "cm"),
            ("Pinky finger stretch",
                *_build_entry_slider_pair(
                    settings.pinky_stretch_ref,
                    min=0,
                    max=1.5,
                    spin_box_step=0.05,
                    parent=size_box,
                ), "cm"),
            ("Vowels offset",
                *_build_entry_slider_pair(
                    settings.vowel_set_offset_fac_ref,
                    min=0,
                    max=1.5,
                    spin_box_step=0.05,
                    parent=size_box,
                ), ""),
            ("Main rows angle",
                *_build_entry_slider_pair(
                    settings.main_rows_angle_ref,
                    min=0,
                    max=45,
                    spin_box_step=0.5,
                    parent=size_box,
                ), "°"),
            ("Vowel rows angle",
                *_build_entry_slider_pair(
                    settings.vowel_rows_angle_ref,
                    min=0,
                    max=75,
                    spin_box_step=0.5,
                    parent=size_box,
                ), "°"),
        )):
            size_box_layout.addWidget(QLabel(label), window_box_index * 2, 0, 1, 3)
            size_box_layout.addWidget(slider, window_box_index * 2 + 1, 0)
            size_box_layout.addWidget(box, window_box_index * 2 + 1, 1)
            size_box_layout.addWidget(QLabel(after_label), window_box_index * 2 + 1, 2)


        compound_key_box, compound_key_slider = compound_input_pair
        @watch_many(settings.key_width_ref.change, settings.key_height_ref.change)
        def set_compound_key_size_max():
            new_max = min(settings.key_width, settings.key_height)

            compound_key_box.setMaximum(new_max)
            compound_key_slider.max = new_max
            

        window_box_index += 1

        size_box_layout.addWidget(QLabel("Column stagger factors"), window_box_index * 2, 0, 1, 3)

        stagger_layout = QGridLayout()
        stagger_layout.setContentsMargins(0, 0, 0, 0)
        stagger_layout.setRowMinimumHeight(0, 120)
        for stagger_index, ref in enumerate((
            settings.index_stagger_fac_ref,
            settings.middle_stagger_fac_ref,
            settings.ring_stagger_fac_ref,
            settings.pinky_stagger_fac_ref,
        )):
            entry, slider = _build_entry_slider_pair(
                ref,
                min=0,
                max=2,
                spin_box_step=0.05,
                slider_orientation=Qt.Vertical,
                parent=size_box,
            )

            stagger_layout.addWidget(slider, 0, stagger_index, Qt.AlignHCenter)
            stagger_layout.addWidget(entry, 1, stagger_index, Qt.AlignHCenter)

        size_box_layout.addLayout(stagger_layout, window_box_index * 2 + 1, 0, 1, 3)
        
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
        layout.addWidget(window_box, 2, 0)
        layout.addWidget(size_box, 0, 1, 4, 1)
        layout.setRowStretch(3, 1)
        layout.addWidget(label_resizing, 4, 0, 1, 2)
        layout.addWidget(label_troubleshooting, 5, 0, 1, 2)
        # layout.addWidget(sizes_box)
        self.setLayout(layout)



def _build_entry_slider_pair(
    ref: Ref[float],
    min: float=0,
    max: float=1,
    spin_box_step=0.1,
    slider_orientation: Qt.Orientation=Qt.Horizontal,
    parent: QWidget=None,
) -> tuple[FloatEntry, FloatSlider]:
    entry = FloatEntry(ref.value,
            min=min,
            max=max,
            spin_step=spin_box_step,
            parent=parent)
    slider = FloatSlider(ref.value,
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
        ref.set(value)

    @on(ref.change)
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
