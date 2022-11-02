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

# [keys], label, (row, column, rowSpan?, columnSpan?)
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
_KEY_SIZE_NUM_BAR = 0.95
KEY_WIDTH = 2
_COMPOUND_KEY_SIZE = 0.95

_KEY_HEIGHT = 2
_REDUCED_KEY_WIDTH = KEY_WIDTH - _COMPOUND_KEY_SIZE / 2
_REDUCED_KEY_HEIGHT = _KEY_HEIGHT - _COMPOUND_KEY_SIZE / 2

_INDEX_STRETCH = KEY_WIDTH * 0.1
_PINKY_STRETCH = KEY_WIDTH * 0.5

_ROW_HEIGHTS = (
    _KEY_SIZE_NUM_BAR,
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_HEIGHT,  # top row
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_HEIGHT,  # bottom row
)

_COL_WIDTHS = (
    KEY_WIDTH + _PINKY_STRETCH,
) + (
    KEY_WIDTH,
) * 2 + (
    _REDUCED_KEY_WIDTH + _INDEX_STRETCH,  # H-, R-
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_WIDTH * 2 + KEY_WIDTH * 2.5,  # *
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_WIDTH + _INDEX_STRETCH,  # -F, -R
) + (
    KEY_WIDTH,
) * 2 + (
    _REDUCED_KEY_WIDTH + _PINKY_STRETCH,  # -T, -S
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_WIDTH,  # -D, -Z
)

_VOWEL_SET_WIDTHS = (
    _REDUCED_KEY_WIDTH,
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_WIDTH,
)

_ROWS_GAP = _KEY_HEIGHT * 1.25

_COL_OFFSETS = (
    0,  # S-
    KEY_WIDTH * 0.375, # T-, K-
    KEY_WIDTH * 0.6, # P-, W-
    0, # H-, R-
) + (
    0,
) * 3 + (
    0,  # -F, -R
    KEY_WIDTH * 0.6,  # -P, -B
    KEY_WIDTH * 0.375,  # -L, -G
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
        _COL_WIDTHS,
        _COL_OFFSETS,
    )):
        column_layout = QVBoxLayout()
        column_layout.addStretch(1)

        row_pos = 0

        for values, label, *rest in column:
            row_span: int = rest[0] if len(rest) > 0 else 1
            row_heights_cm = _ROW_HEIGHTS[row_pos:row_pos + row_span]


            key_widget = KeyWidget(values, label, keyboard_widget)
            key_widgets.append(key_widget)

            if len(rest) > 1:
                num_bar_label: str = rest[1]
                keyboard_widget.num_bar_pressed_change.connect(key_widget.num_bar_pressed_handler(label, num_bar_label))


            if row_pos <= _LOW_ROW < row_pos + row_span:
                row_heights_cm = (*row_heights_cm, col_offset_cm / 2)


            if col_index == _ASTERISK_COLUMN_INDEX:
                def resize(
                    key_widget: KeyWidget=key_widget,
                    col_width_cm: float=col_width_cm,
                    row_heights_cm: tuple[float]=row_heights_cm,
                ):
                    key_widget.setMinimumWidth(dpi.cm(col_width_cm))
                    key_widget.setFixedHeight(sum(dpi.cm(height) for height in row_heights_cm))

                    # Defer setting the minimum width to later; setting it immediately causes it to shrink to this size initially
                    QTimer.singleShot(0, lambda: key_widget.setMinimumWidth(0))
                    
            else:
                def resize(
                    key_widget: KeyWidget=key_widget,
                    col_width_cm: float=col_width_cm,
                    row_heights_cm: tuple[float]=row_heights_cm,
                ):
                    key_widget.setFixedSize(dpi.cm(col_width_cm), sum(dpi.cm(height) for height in row_heights_cm))

            resize()
            dpi.change.connect(resize)


            column_layout.addWidget(key_widget)

            row_pos += row_span
            
        column_spacer = QSpacerItem(0, 0)
        column_layout.addSpacerItem(column_spacer)
        def resize_column_spacing(
            column_spacer: QSpacerItem=column_spacer,
            col_offset_cm: float=col_offset_cm,
        ):
            column_spacer.changeSize(0, dpi.cm(col_offset_cm / 2))
        resize_column_spacing()
        dpi.change.connect(resize_column_spacing)

        
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

    for i, size_cm in enumerate(_ROW_HEIGHTS):
        layout.setRowMinimumHeight(i, dpi.cm(size_cm))
        layout.setRowStretch(i, 0)

    for i, size_cm in enumerate(_COL_WIDTHS):
        layout.setColumnMinimumWidth(i, dpi.cm(size_cm))
        layout.setColumnStretch(i, 0)

    # * column
    layout.setColumnStretch(_ASTERISK_COLUMN_INDEX, 1)
    QTimer.singleShot(0, lambda: layout.setColumnMinimumWidth(_ASTERISK_COLUMN_INDEX, 0))


    def resize_columns():
        for i, size_cm in enumerate(_ROW_HEIGHTS):
            layout.setRowMinimumHeight(i, dpi.cm(size_cm))

        for i, size_cm in enumerate(_COL_WIDTHS):
            layout.setColumnMinimumWidth(i, dpi.cm(size_cm))

        # * column
        QTimer.singleShot(0, lambda: layout.setColumnMinimumWidth(_ASTERISK_COLUMN_INDEX, 0))
    
    dpi.change.connect(resize_columns)


    layout.setSpacing(0)


    return layout


def _build_vowel_row_layout(keyboard_widget: KeyboardWidget, key_widgets: list[KeyWidget]) -> QLayout:
    # Parameter defaults on inner functions are used to create closures

    dpi = keyboard_widget.dpi
    
    layout = QHBoxLayout()
    layout.setSpacing(0)

    def add_vowel_set(vowel_key_descriptors):
        for (values, label, *rest), width in zip(vowel_key_descriptors, _VOWEL_SET_WIDTHS):
            key_widget = KeyWidget(values, label, keyboard_widget)
            key_widgets.append(key_widget)
        
            if len(rest) > 0:
                num_bar_label: str = rest[0]
                keyboard_widget.num_bar_pressed_change.connect(key_widget.num_bar_pressed_handler(label, num_bar_label))


            def resize(
                key_widget: KeyWidget=key_widget,
                width: float=width,
            ):
                key_widget.setFixedSize(dpi.cm(width), dpi.cm(_KEY_HEIGHT))

            resize()
            dpi.change.connect(resize)


            layout.addWidget(key_widget)

    
    layout.addSpacing(0)
    add_vowel_set(_VOWEL_ROW_KEYS_LEFT)
    layout.addStretch(1)
    add_vowel_set(_VOWEL_ROW_KEYS_RIGHT)
    layout.addSpacing(0)

    def resize_spacing():
        # TODO make the spacing amount here a constant?
        layout.itemAt(0).spacerItem().changeSize(dpi.cm(KEY_WIDTH) * 3.375, 0)
        layout.itemAt(layout.count() - 1).spacerItem().changeSize(dpi.cm(KEY_WIDTH) * 4.375, 0)

    resize_spacing()
    dpi.change.connect(resize_spacing)


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
    def resize_row_spacer():
        layout.setRowMinimumHeight(1, dpi.cm(_ROWS_GAP))
        QTimer.singleShot(0, lambda: layout.setRowMinimumHeight(1, 0))
    resize_row_spacer()
    dpi.change.connect(resize_row_spacer)

    layout.addLayout(build_vowel_row(keyboard_widget, key_widgets), 2, 0)

    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    return layout


#region Exports

build_keyboard = {
    KeyLayout.STAGGERED: partial(_build_keyboard_layout, _build_main_rows_layout_staggered, _build_vowel_row_layout),
    KeyLayout.GRID: partial(_build_keyboard_layout, _build_main_rows_layout_grid, _build_vowel_row_layout),
}

#endregion