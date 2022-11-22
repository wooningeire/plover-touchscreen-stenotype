from PyQt5.QtCore import (
    QTimer,
)
from PyQt5.QtWidgets import (
    QLayout,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
)

from functools import partial
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from plover_touchscreen_stenotype.widgets.KeyboardWidget import KeyboardWidget
else:
    KeyboardWidget = object

from plover_touchscreen_stenotype.widgets.KeyWidget import KeyWidget
from plover_touchscreen_stenotype.settings import KeyLayout
from plover_touchscreen_stenotype.util import Ref, computed, on, on_many, watch, watch_many


_TOP_ROW = 2
_LOW_ROW = 4
_TOP_COMPOUND_ROW = 1
_LOW_COMPOUND_ROW = 3

# [keys], label, rowSpan?, numberLabel?
_MAIN_ROWS_KEYS = (
    (
        (["#"], ""),
        (["#", "S-"], ""),
        (["S-"], "S", 3, "1"),
    ), (
        (["#"], ""),
        (["#", "T-"], ""),
        (["T-"], "T", 1, "2"),
        (["T-", "K-"], ""),
        (["K-"], "K"),
    ), (
        (["#"], ""),
        (["#", "P-"], ""),
        (["P-"], "P", 1, "3"),
        (["P-", "W-"], ""),
        (["W-"], "W"),
    ), (
        (["#"], ""),
        (["#", "H-"], ""),
        (["H-"], "H", 1, "4"),
        (["H-", "R-"], ""),
        (["R-"], "R"),
    ), (
        (["#"], ""),
        (["#", "H-", "*"], ""),
        (["H-", "*"], ""),
        (["H-", "R-", "*"], ""),
        (["R-", "*"], ""),
    ), (
        (["#"], "#"),
        (["#", "*"], ""),
        (["*"], "*", 3),
    ), (
        (["#"], ""),
        (["#", "*", "-F"], ""),
        (["*", "-F"], ""),
        (["*", "-F", "-R"], ""),
        (["*", "-R"], ""),
    ), (
        (["#"], ""),
        (["#", "-F"], ""),
        (["-F"], "F", 1, "6"),
        (["-F", "-R"], ""),
        (["-R"], "R"),
    ), (
        (["#"], ""),
        (["#", "-P"], ""),
        (["-P"], "P", 1, "7"),
        (["-P", "-B"], ""),
        (["-B"], "B"),
    ), (
        (["#"], ""),
        (["#", "-L"], ""),
        (["-L"], "L", 1, "8"),
        (["-L", "-G"], ""),
        (["-G"], "G"),
    ), (
        (["#"], ""),
        (["#", "-T"], ""),
        (["-T"], "T", 1, "9"),
        (["-T", "-S"], ""),
        (["-S"], "S"),
    ), (
        (["#"], ""),
        (["#", "-T", "-D"], ""),
        (["-T", "-D"], ""),
        (["-T", "-S", "-D", "-Z"], ""),
        (["-S", "-Z"], ""),
    ), (
        (["#"], ""),
        (["#", "-D"], ""),
        (["-D"], "D"),
        (["-D", "-Z"], ""),
        (["-Z"], "Z"),
    ),
)

# [keys], label, (row, column, rowSpan?, columnSpan?), numberLabel?
_MAIN_ROWS_KEYS_GRID = (
    (["#"], "#", (0, 0, 1, -1)),
    (["S-"], "S", (_TOP_ROW, 0, 3, 1), "1"),
    (["T-"], "T", (_TOP_ROW, 1), "2"),
    (["K-"], "K", (_LOW_ROW, 1)),
    (["P-"], "P", (_TOP_ROW, 2), "3"),
    (["W-"], "W", (_LOW_ROW, 2)),
    (["H-"], "H", (_TOP_ROW, 3), "4"),
    (["R-"], "R", (_LOW_ROW, 3)),
    (["H-", "*"], "", (_TOP_ROW, 4)),
    (["R-", "*"], "", (_LOW_ROW, 4)),
    (["*"], "*", (_TOP_ROW, 5, 3, 1)),
    (["*", "-F"], "", (_TOP_ROW, 6)),
    (["*", "-R"], "", (_LOW_ROW, 6)),
    (["-F"], "F", (_TOP_ROW, 7), "6"),
    (["-R"], "R", (_LOW_ROW, 7)),
    (["-P"], "P", (_TOP_ROW, 8), "7"),
    (["-B"], "B", (_LOW_ROW, 8)),
    (["-L"], "L", (_TOP_ROW, 9), "8"),
    (["-G"], "G", (_LOW_ROW, 9)),
    (["-T"], "T", (_TOP_ROW, 10), "9"),
    (["-S"], "S", (_LOW_ROW, 10)),
    (["-T", "-D"], "", (_TOP_ROW, 11)),
    (["-S", "-Z"], "", (_LOW_ROW, 11)),
    (["-D"], "D", (_TOP_ROW, 12)),
    (["-Z"], "Z", (_LOW_ROW, 12)),

    (["#", "S-"], "", (_TOP_COMPOUND_ROW, 0)),
    (["#", "T-"], "", (_TOP_COMPOUND_ROW, 1)),
    (["#", "P-"], "", (_TOP_COMPOUND_ROW, 2)),
    (["#", "H-"], "", (_TOP_COMPOUND_ROW, 3)),
    (["#", "H-", "*"], "", (_TOP_COMPOUND_ROW, 4)),
    (["#", "*"], "", (_TOP_COMPOUND_ROW, 5)),
    (["#", "*", "-F"], "", (_TOP_COMPOUND_ROW, 6)),
    (["#", "-F"], "", (_TOP_COMPOUND_ROW, 7)),
    (["#", "-P"], "", (_TOP_COMPOUND_ROW, 8)),
    (["#", "-L"], "", (_TOP_COMPOUND_ROW, 9)),
    (["#", "-T"], "", (_TOP_COMPOUND_ROW, 10)),
    (["#", "-T", "-D"], "", (_TOP_COMPOUND_ROW, 11)),
    (["#", "-D"], "", (_TOP_COMPOUND_ROW, 12)),

    (["T-", "K-"], "", (_LOW_COMPOUND_ROW, 1)),
    (["P-", "W-"], "", (_LOW_COMPOUND_ROW, 2)),
    (["H-", "R-"], "", (_LOW_COMPOUND_ROW, 3)),
    (["H-", "R-", "*"], "", (_LOW_COMPOUND_ROW, 4)),
    (["*", "-R", "-F"], "", (_LOW_COMPOUND_ROW, 6)),
    (["-F", "-R"], "", (_LOW_COMPOUND_ROW, 7)),
    (["-P", "-B"], "", (_LOW_COMPOUND_ROW, 8)),
    (["-L", "-G"], "", (_LOW_COMPOUND_ROW, 9)),
    (["-T", "-S"], "", (_LOW_COMPOUND_ROW, 10)),
    (["-T", "-S", "-D", "-Z"], "", (_LOW_COMPOUND_ROW, 11)),
    (["-D", "-Z"], "", (_LOW_COMPOUND_ROW, 12)),
)

_VOWEL_ROW_KEYS_LEFT = (
    (["A-"], "A", "5"),
    (["A-", "O-"], ""),
    (["O-"], "O", "0"),
)

_VOWEL_ROW_KEYS_RIGHT = (
    (["-E"], "E"),
    (["-E", "-U"], ""),
    (["-U"], "U"),
)

# in centimeters
key_width = Ref(2)
_key_height = Ref(2.25)
_compound_key_size = Ref(0.9)

_reduced_key_width = computed(lambda: key_width.value - _compound_key_size.value / 2, key_width, _compound_key_size)
_reduced_key_height = computed(lambda: _key_height.value - _compound_key_size.value / 2, _key_height, _compound_key_size)

_key_height_num_bar = computed(lambda: _key_height.value / 2, _key_height)

_index_stretch = Ref(0.2)
_pinky_stretch = Ref(0.8)

_VOWEL_SET_OFFSET = 0.875

_row_heights = (
    _key_height_num_bar,
    _compound_key_size,
    _reduced_key_height,  # top row
    _compound_key_size,
    _reduced_key_height,  # bottom row
)

_col_widths = (
    computed(lambda: key_width.value + _pinky_stretch.value, key_width, _pinky_stretch),
    key_width,
    key_width,
    computed(lambda: _reduced_key_width.value + _index_stretch.value, _reduced_key_width, _index_stretch),  # H-, R-
    _compound_key_size,
    computed(lambda: _reduced_key_width.value * 2 + key_width.value * 2.5, _reduced_key_width, key_width),  # *
    _compound_key_size,
    computed(lambda: _reduced_key_width.value + _index_stretch.value, _reduced_key_width, _index_stretch),  # -F, -R
    key_width,
    key_width,
    computed(lambda: _reduced_key_width.value + _pinky_stretch.value, _reduced_key_width, _pinky_stretch),  # -T, -S
    _compound_key_size,
    _reduced_key_width,  # -D, -Z
)

_vowel_set_widths = (
    _reduced_key_width,
    _compound_key_size,
    _reduced_key_width,
)

_ROWS_GAP = 2.25

_COL_OFFSETS = (
    0,  # S-
    key_width.value * 0.375, # T-, K-
    key_width.value * 0.6, # P-, W-
    0, # H-, R-
    0,
    0,
    0,
    0,  # -F, -R
    key_width.value * 0.6,  # -P, -B
    key_width.value * 0.375,  # -L, -G
    0,  # -T, -S
    0,
    0, # -D, -Z
)


_ASTERISK_COLUMN_INDEX = 5



def _build_main_rows_layout_staggered(keyboard_widget: KeyboardWidget, key_widgets: list[KeyWidget]) -> QLayout:
    # Parameter defaults on inner functions are used to create closures

    dpi = keyboard_widget.dpi

    layout = QHBoxLayout()
    for col_index, (column, col_width_cm, col_offset_cm) in enumerate(zip(
        _MAIN_ROWS_KEYS,
        _col_widths,
        _COL_OFFSETS,
    )):
        column_layout = QVBoxLayout()
        column_layout.addStretch(1)

        row_pos = 0

        for values, label, *rest in column:
            row_span: int = rest[0] if len(rest) > 0 else 1
            row_heights_cm = _row_heights[row_pos:row_pos + row_span]


            key_widget = KeyWidget(values, label, keyboard_widget)
            key_widgets.append(key_widget)

            if len(rest) > 1:
                num_bar_label: str = rest[1]
                keyboard_widget.num_bar_pressed_change.connect(key_widget.num_bar_pressed_handler(label, num_bar_label))


            if row_pos <= _LOW_ROW < row_pos + row_span:
                row_heights_cm = (*row_heights_cm, Ref(col_offset_cm / 2))

            if col_index == _ASTERISK_COLUMN_INDEX:
                @watch_many(dpi.change, *(height.change for height in row_heights_cm), parent=key_widget)
                def resize(
                    key_widget: KeyWidget=key_widget,
                    col_width_cm: Ref[float]=col_width_cm,
                    row_heights_cm: tuple[Ref[float]]=row_heights_cm,
                ):
                    key_widget.setMinimumWidth(dpi.cm(col_width_cm.value))
                    key_widget.setFixedHeight(sum(dpi.cm(height.value) for height in row_heights_cm))

                    # Defer setting the minimum width to later; setting it immediately causes it to shrink to this size initially
                    QTimer.singleShot(0, lambda: key_widget.setMinimumWidth(0))
                    
            else:
                @watch_many(dpi.change, col_width_cm.change, *(height.change for height in row_heights_cm), parent=key_widget)
                def resize(
                    key_widget: KeyWidget=key_widget,
                    col_width_cm: Ref[float]=col_width_cm,
                    row_heights_cm: tuple[Ref[float]]=row_heights_cm,
                ):
                    key_widget.setFixedSize(dpi.cm(col_width_cm.value), sum(dpi.cm(height.value) for height in row_heights_cm))


            column_layout.addWidget(key_widget)

            row_pos += row_span
            
        column_spacer = QSpacerItem(0, 0)
        column_layout.addSpacerItem(column_spacer)

        @watch(dpi.change, parent=column_layout)
        def resize_column_spacing(
            column_spacer: QSpacerItem=column_spacer,
            col_offset_cm: float=col_offset_cm,
        ):
            column_spacer.changeSize(0, dpi.cm(col_offset_cm / 2))

        
        layout.addLayout(column_layout)

        # if i in (0, 9): # S- and -L, -G
        #     layout.addSpacing(dpi.px(_PINKY_STRETCH))
        if col_index == _ASTERISK_COLUMN_INDEX:
            layout.setStretchFactor(column_layout, 1)


    # def resize_asterisk_column():
    #     asterisk_column = layout.itemAt(_ASTERISK_COLUMN_INDEX).layout()
    #     for item in (asterisk_column.itemAt(i) for i in range(asterisk_column.count())):
    #         if not (widget := item.widget()): continue
    #         widget.setMinimumWidth(0)

    # QTimer.singleShot(0, resize_asterisk_column)
        

    layout.setSpacing(0)


    return layout


def _build_main_rows_layout_grid(keyboard_widget: KeyboardWidget, key_widgets: list[KeyWidget]) -> QLayout:
    dpi = keyboard_widget.dpi

    layout = QGridLayout()
    for values, label, grid_position, *rest in _MAIN_ROWS_KEYS_GRID:
        key_widget = KeyWidget(values, label, keyboard_widget)
        key_widgets.append(key_widget)
        
        if len(rest) > 0:
            num_bar_label: str = rest[0]
            keyboard_widget.num_bar_pressed_change.connect(key_widget.num_bar_pressed_handler(label, num_bar_label))

        layout.addWidget(key_widget, *grid_position)

    for i, size_cm in enumerate(_row_heights):
        layout.setRowMinimumHeight(i, dpi.cm(size_cm.value))
        layout.setRowStretch(i, 0)

    for i, size_cm in enumerate(_col_widths):
        layout.setColumnMinimumWidth(i, dpi.cm(size_cm.value))
        layout.setColumnStretch(i, 0)


    layout.setColumnStretch(_ASTERISK_COLUMN_INDEX, 1)
    @watch(dpi.change, parent=layout)
    def resize_asterisk_column():
        QTimer.singleShot(0, lambda: layout.setColumnMinimumWidth(_ASTERISK_COLUMN_INDEX, 0))


    @on_many(dpi.change, *(height.change for height in _row_heights), *(width.change for width in _col_widths), parent=layout)
    def resize_columns():
        for i, size_cm in enumerate(_row_heights):
            layout.setRowMinimumHeight(i, dpi.cm(size_cm.value))

        for i, size_cm in enumerate(_col_widths):
            if i == _ASTERISK_COLUMN_INDEX: continue
            layout.setColumnMinimumWidth(i, dpi.cm(size_cm.value))


    layout.setSpacing(0)


    return layout


def _build_vowel_row_layout(keyboard_widget: KeyboardWidget, key_widgets: list[KeyWidget]) -> QLayout:
    # Parameter defaults on inner functions are used to create closures

    dpi = keyboard_widget.dpi
    
    layout = QHBoxLayout()
    layout.setSpacing(0)

    def add_vowel_set(vowel_key_descriptors):
        for (values, label, *rest), width in zip(vowel_key_descriptors, _vowel_set_widths):
            key_widget = KeyWidget(values, label, keyboard_widget)
            key_widgets.append(key_widget)
        
            if len(rest) > 0:
                num_bar_label: str = rest[0]
                keyboard_widget.num_bar_pressed_change.connect(key_widget.num_bar_pressed_handler(label, num_bar_label))


            @watch_many(dpi.change, width.change, _key_height.change, parent=key_widget)
            def resize(
                key_widget: KeyWidget=key_widget,
                width: Ref[float]=width,
            ):
                key_widget.setFixedSize(dpi.cm(width.value), dpi.cm(_key_height.value))


            layout.addWidget(key_widget)

    
    layout.addSpacerItem(left_spacer := QSpacerItem(0, 0))
    add_vowel_set(_VOWEL_ROW_KEYS_LEFT)
    layout.addStretch(1)
    add_vowel_set(_VOWEL_ROW_KEYS_RIGHT)
    layout.addSpacerItem(right_spacer := QSpacerItem(0, 0))

    @watch_many(dpi.change, key_width.change, _pinky_stretch.change, _index_stretch.change, parent=layout)
    def resize_spacing():
        left_bank_width = dpi.cm(key_width.value) * 4 + dpi.cm(_pinky_stretch.value) + dpi.cm(_index_stretch.value)
        right_bank_width = left_bank_width + dpi.cm(key_width.value)

        left_spacer.changeSize(left_bank_width - dpi.cm(key_width.value) - dpi.cm(_VOWEL_SET_OFFSET), 0)
        right_spacer.changeSize(right_bank_width - dpi.cm(key_width.value) - dpi.cm(_VOWEL_SET_OFFSET), 0)

    @on(key_width.change, parent=layout)
    def invalidate_layout():
        layout.invalidate()


    return layout


def _build_keyboard_layout(
    build_main_rows: Callable[[KeyboardWidget, list[KeyWidget]], QLayout],
    build_vowel_row: Callable[[KeyboardWidget, list[KeyWidget]], QLayout],
    keyboard_widget: KeyboardWidget,
    key_widgets: list[KeyWidget],
) -> QLayout:
    dpi = keyboard_widget.dpi
    
    # QVBoxLayout has an odd side effect when window is resized to a large enough height; the main rows layout would
    # start to grow along with the spacer item
    layout = QGridLayout()

    layout.addLayout(build_main_rows(keyboard_widget, key_widgets), 0, 0)

    layout.setRowStretch(1, 1)
    
    @watch(dpi.change)
    def resize_row_spacer():
        layout.setRowMinimumHeight(1, dpi.cm(_ROWS_GAP))
        QTimer.singleShot(0, lambda: layout.setRowMinimumHeight(1, 0))

    layout.addLayout(build_vowel_row(keyboard_widget, key_widgets), 2, 0)

    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)


    # temp
    @on(keyboard_widget.settings.key_width_change, parent=layout)
    def set_key_width(value: float):
        key_width.value = value

    @on(keyboard_widget.settings.key_height_change, parent=layout)
    def set_key_height(value: float):
        _key_height.value = value

    @on(keyboard_widget.settings.compound_key_size_change, parent=layout)
    def set_compund_key_size(value: float):
        _compound_key_size.value = value

    @on(keyboard_widget.settings.index_stretch_change, parent=layout)
    def set_index_stretch(value: float):
        _index_stretch.value = value

    @on(keyboard_widget.settings.pinky_stretch_change, parent=layout)
    def set_pinky_stretch(value: float):
        _pinky_stretch.value = value

    return layout


#region Exports

build_keyboard = {
    KeyLayout.STAGGERED: partial(_build_keyboard_layout, _build_main_rows_layout_staggered, _build_vowel_row_layout),
    KeyLayout.GRID: partial(_build_keyboard_layout, _build_main_rows_layout_grid, _build_vowel_row_layout),
}

#endregion