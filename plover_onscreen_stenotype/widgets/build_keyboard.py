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
    from plover_onscreen_stenotype.widgets.KeyboardWidget import KeyboardWidget
else:
    KeyboardWidget = object

from plover_onscreen_stenotype.widgets.KeyWidget import KeyWidget
from plover_onscreen_stenotype.settings import KeyLayout


_TOP_ROW = 2
_LOW_ROW = 4
_TOP_COMPOUND_ROW = 1
_LOW_COMPOUND_ROW = 3

_MAIN_ROWS_KEYS = (
    (
        (["#"], ""),
        (["#", "S-"], ""),
        (["S-"], "S", 3),
    ), (
        (["#"], ""),
        (["#", "T-"], ""),
        (["T-"], "T"),
        (["T-", "K-"], ""),
        (["K-"], "K"),
    ), (
        (["#"], ""),
        (["#", "P-"], ""),
        (["P-"], "P"),
        (["P-", "W-"], ""),
        (["W-"], "W"),
    ), (
        (["#"], ""),
        (["#", "H-"], ""),
        (["H-"], "H"),
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
        (["-F"], "F"),
        (["-F", "-R"], ""),
        (["-R"], "R"),
    ), (
        (["#"], ""),
        (["#", "-P"], ""),
        (["-P"], "P"),
        (["-P", "-B"], ""),
        (["-B"], "B"),
    ), (
        (["#"], ""),
        (["#", "-L"], ""),
        (["-L"], "L"),
        (["-L", "-G"], ""),
        (["-G"], "G"),
    ), (
        (["#"], ""),
        (["#", "-T"], ""),
        (["-T"], "T"),
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

# [keys], (row, column, rowSpan, columnSpan)
_MAIN_ROWS_KEYS_GRID = (
    (["#"], "#", (0, 0, 1, -1)),
    (["S-"], "S", (_TOP_ROW, 0, 3, 1)),
    (["T-"], "T", (_TOP_ROW, 1)),
    (["K-"], "K", (_LOW_ROW, 1)),
    (["P-"], "P", (_TOP_ROW, 2)),
    (["W-"], "W", (_LOW_ROW, 2)),
    (["H-"], "H", (_TOP_ROW, 3)),
    (["R-"], "R", (_LOW_ROW, 3)),
    (["H-", "*"], "", (_TOP_ROW, 4)),
    (["R-", "*"], "", (_LOW_ROW, 4)),
    (["*"], "*", (_TOP_ROW, 5, 3, 1)),
    (["*", "-F"], "", (_TOP_ROW, 6)),
    (["*", "-R"], "", (_LOW_ROW, 6)),
    (["-F"], "F", (_TOP_ROW, 7)),
    (["-R"], "R", (_LOW_ROW, 7)),
    (["-P"], "P", (_TOP_ROW, 8)),
    (["-B"], "B", (_LOW_ROW, 8)),
    (["-L"], "L", (_TOP_ROW, 9)),
    (["-G"], "G", (_LOW_ROW, 9)),
    (["-T"], "T", (_TOP_ROW, 10)),
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
    (["A-"], "A"),
    (["A-", "O-"], ""),
    (["O-"], "O"),
)

_VOWEL_ROW_KEYS_RIGHT = (
    (["-E"], "E"),
    (["-E", "-U"], ""),
    (["-U"], "U"),
)

# in centimeters
_KEY_SIZE_NUM_BAR = 0.96890420899
_KEY_SIZE = 1.8
_COMPOUND_KEY_SIZE = 0.91507619738
_REDUCED_KEY_SIZE = _KEY_SIZE - _COMPOUND_KEY_SIZE / 2

_PINKY_STRETCH = _KEY_SIZE * 0.125

_ROW_HEIGHTS = (
    _KEY_SIZE_NUM_BAR,
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_SIZE,  # top row
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_SIZE,  # bottom row
)

_COL_WIDTHS = (
    _KEY_SIZE + _PINKY_STRETCH,
) + (
    _KEY_SIZE,
) * 2 + (
    _REDUCED_KEY_SIZE,  # H-, R-
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_SIZE * 2 + _KEY_SIZE * 2.5,  # *
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_SIZE,  # -F, -R
) + (
    _KEY_SIZE,
) * 2 + (
    _REDUCED_KEY_SIZE + _PINKY_STRETCH,  # -T, -S
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_SIZE,  # -D, -Z
)

_VOWEL_SET_WIDTHS = (
    _REDUCED_KEY_SIZE,
    _COMPOUND_KEY_SIZE,
    _REDUCED_KEY_SIZE,
)

_ROWS_GAP = _KEY_SIZE * 0.85

_COL_OFFSETS = (
    0,  # S-
    _KEY_SIZE * 0.35, # T-, K-
    _KEY_SIZE * 0.6, # P-, W-
    0, # H-, R-
) + (
    0,
) * 3 + (
    0,  # -F, -R
    _KEY_SIZE * 0.6,  # -P, -B
    _KEY_SIZE * 0.35,  # -L, -G
    0,  # -T, -S
    0,
    0, # -D, -Z
)


_ASTERISK_COLUMN_INDEX = 5



def _build_main_rows_layout_staggered(keyboard_widget: KeyboardWidget, key_widgets: list[KeyWidget]) -> QLayout:
    # Parameter defaults on inner functions are used to create closures

    layout = QHBoxLayout()
    for i, (column, col_width_cm, col_offset_cm) in enumerate(zip(
        _MAIN_ROWS_KEYS,
        _COL_WIDTHS,
        _COL_OFFSETS,
    )):
        column_layout = QVBoxLayout()
        column_layout.addStretch(1)

        row_pos = 0

        for values, label, *rest in column:
            row_span = rest[0] if rest else 1
            row_heights_cm = _ROW_HEIGHTS[row_pos:row_pos + row_span]

            key_widget = KeyWidget(values, label, keyboard_widget)
            key_widgets.append(key_widget)


            if i == _ASTERISK_COLUMN_INDEX:
                def resize(
                    key_widget: KeyWidget=key_widget,
                    col_width_cm: float=col_width_cm,
                    row_heights_cm: tuple[float]=row_heights_cm,
                ):
                    key_widget.setMinimumWidth(keyboard_widget.px(col_width_cm))
                    key_widget.setFixedHeight(sum(keyboard_widget.px(height) for height in row_heights_cm))

                    # Defer setting the minimum width to later; setting it immediately causes it to shrink to this size initially
                    QTimer.singleShot(0, lambda: key_widget.setMinimumWidth(0))
                    
            else:
                def resize(
                    key_widget: KeyWidget=key_widget,
                    col_width_cm: float=col_width_cm,
                    row_heights_cm: tuple[float]=row_heights_cm,
                ):
                    key_widget.setFixedSize(keyboard_widget.px(col_width_cm), sum(keyboard_widget.px(height) for height in row_heights_cm))

            resize()
            keyboard_widget.dpi_change.connect(resize)


            column_layout.addWidget(key_widget)

            row_pos += row_span
            
        
        column_layout.addSpacing(keyboard_widget.px(col_offset_cm))

        column_spacer = column_layout.itemAt(column_layout.count() - 1).spacerItem()
        def resize_column_spacing(
            column_spacer: QSpacerItem=column_spacer,
            col_offset_cm: float=col_offset_cm,
        ):
            column_spacer.changeSize(0, keyboard_widget.px(col_offset_cm))
        keyboard_widget.dpi_change.connect(resize_column_spacing)

        
        layout.addLayout(column_layout)

        # if i in (0, 9): # S- and -L, -G
        #     layout.addSpacing(keyboard_widget.px(_PINKY_STRETCH))
        if i == _ASTERISK_COLUMN_INDEX:
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
    layout = QGridLayout()
    for (values, label, grid_position) in _MAIN_ROWS_KEYS_GRID:
        key_widget = KeyWidget(values, label, keyboard_widget)
        key_widgets.append(key_widget)

        layout.addWidget(key_widget, *grid_position)

    for i, size_cm in enumerate(_ROW_HEIGHTS):
        layout.setRowMinimumHeight(i, keyboard_widget.px(size_cm))
        layout.setRowStretch(i, 0)

    for i, size_cm in enumerate(_COL_WIDTHS):
        layout.setColumnMinimumWidth(i, keyboard_widget.px(size_cm))
        layout.setColumnStretch(i, 0)

    # * column
    layout.setColumnStretch(_ASTERISK_COLUMN_INDEX, 1)
    QTimer.singleShot(0, lambda: layout.setColumnMinimumWidth(_ASTERISK_COLUMN_INDEX, 0))


    def resize_columns():
        for i, size_cm in enumerate(_ROW_HEIGHTS):
            layout.setRowMinimumHeight(i, keyboard_widget.px(size_cm))

        for i, size_cm in enumerate(_COL_WIDTHS):
            layout.setColumnMinimumWidth(i, keyboard_widget.px(size_cm))

        # * column
        QTimer.singleShot(0, lambda: layout.setColumnMinimumWidth(_ASTERISK_COLUMN_INDEX, 0))
    
    keyboard_widget.dpi_change.connect(resize_columns)


    layout.setSpacing(0)


    return layout


def _build_vowel_row_layout(keyboard_widget: KeyboardWidget, key_widgets: list[KeyWidget]) -> QLayout:
    # Parameter defaults on inner functions are used to create closures

    layout = QHBoxLayout()

    layout.setSpacing(0)

    def add_vowel_set(vowel_key_descriptors):
        for ((values, label), width) in zip(vowel_key_descriptors, _VOWEL_SET_WIDTHS):
            key_widget = KeyWidget(values, label, keyboard_widget)
            key_widgets.append(key_widget)


            def resize(
                key_widget: KeyWidget=key_widget,
                width: float=width,
            ):
                key_widget.setFixedSize(keyboard_widget.px(width), keyboard_widget.px(_KEY_SIZE))

            resize()
            keyboard_widget.dpi_change.connect(resize)


            layout.addWidget(key_widget)

    
    layout.addSpacing(0)
    add_vowel_set(_VOWEL_ROW_KEYS_LEFT)
    layout.addStretch(1)
    add_vowel_set(_VOWEL_ROW_KEYS_RIGHT)
    layout.addSpacing(0)

    def resize_spacing():
        layout.itemAt(0).spacerItem().changeSize(keyboard_widget.px(_KEY_SIZE) * 3 + keyboard_widget.px(_PINKY_STRETCH), 0)
        layout.itemAt(layout.count() - 1).spacerItem().changeSize(keyboard_widget.px(_KEY_SIZE) * 4 + keyboard_widget.px(_PINKY_STRETCH), 0)

    resize_spacing()
    keyboard_widget.dpi_change.connect(resize_spacing)


    return layout


def _build_keyboard_layout(
    build_main_rows: Callable[[KeyboardWidget, list[KeyWidget]], QLayout],
    build_vowel_row: Callable[[KeyboardWidget, list[KeyWidget]], QLayout],
    keyboard_widget: KeyboardWidget,
    key_widgets: list[KeyWidget],
) -> QLayout:
    layout = QVBoxLayout(keyboard_widget)

    layout.addLayout(build_main_rows(keyboard_widget, key_widgets))
    layout.addSpacerItem(QSpacerItem(
        0,
        keyboard_widget.px(_ROWS_GAP),
        QSizePolicy.Preferred,
        QSizePolicy.Expanding,
    ))
    layout.addLayout(build_vowel_row(keyboard_widget, key_widgets))

    
    layout.setSpacing(0)


    return layout


#region Exports

build_keyboard = {
    KeyLayout.STAGGERED: partial(_build_keyboard_layout, _build_main_rows_layout_staggered, _build_vowel_row_layout),
    KeyLayout.GRID: partial(_build_keyboard_layout, _build_main_rows_layout_grid, _build_vowel_row_layout),
}

#endregion