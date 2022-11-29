from PyQt5.QtCore import (
    QTimer,
    Qt,
)
from PyQt5.QtWidgets import (
    QLayout,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSpacerItem,
    QGraphicsScene,
    QWidget,
)

from functools import partial
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from .KeyboardWidget import KeyboardWidget
else:
    KeyboardWidget = object

from .KeyWidget import KeyWidget
from .RotatableKeyContainer import RotatableKeyContainer
from ..settings import Settings, KeyLayout
from ..util import UseDpi, Ref, computed, computed_on_signal, on, on_many, watch, watch_many, KEY_STYLESHEET


_TOP_ROW = 2
_LOW_ROW = 4
_TOP_COMPOUND_ROW = 1
_LOW_COMPOUND_ROW = 3

# [keys], label, rowSpan?, numberLabel?
_MAIN_ROWS_KEYS_LEFT = (
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
        (["*"], "🞱", 3),
    ),
)

_MAIN_ROWS_KEYS_RIGHT = (
    (
        (["#"], "#"),
        (["#", "*"], ""),
        (["*"], "🞱", 3),
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


#region Exports

def use_build_keyboard(settings: Settings, keyboard_widget: KeyboardWidget, dpi: UseDpi):
    # in centimeters
    key_width = settings.key_width_ref
    key_height = settings.key_height_ref
    compound_key_size = settings.compound_key_size_ref

    reduced_key_width = computed(lambda: key_width.value - compound_key_size.value / 2,
            key_width, compound_key_size)
    reduced_key_height = computed(lambda: key_height.value - compound_key_size.value / 2,
            key_height, compound_key_size)

    key_height_num_bar = computed(lambda: key_height.value / 2,
            key_height)

    index_stretch = settings.index_stretch_ref
    pinky_stretch = settings.pinky_stretch_ref

    vowel_set_offset_fac = settings.vowel_set_offset_fac_ref
    vowel_set_offset = computed(lambda: key_width.value * vowel_set_offset_fac.value,
            key_width, vowel_set_offset_fac)

    row_heights = (
        key_height_num_bar,
        compound_key_size,
        reduced_key_height,  # top row
        compound_key_size,
        reduced_key_height,  # bottom row
    )

    reduced_index_width = computed(lambda: reduced_key_width.value + index_stretch.value,
            reduced_key_width, index_stretch)

    col_widths = (
        computed(lambda: key_width.value + pinky_stretch.value,
                key_width, pinky_stretch),
        key_width,
        key_width,
        reduced_index_width,  # H-, R-
        compound_key_size,
        computed(lambda: reduced_key_width.value * 2 + key_width.value * 2.5,
                reduced_key_width, key_width),  # *
        compound_key_size,
        reduced_index_width,  # -F, -R
        key_width,
        key_width,
        computed(lambda: reduced_key_width.value + pinky_stretch.value,
                reduced_key_width, pinky_stretch),  # -T, -S
        compound_key_size,
        reduced_key_width,  # -D, -Z
    )

    col_widths_left = (
        computed(lambda: key_width.value + pinky_stretch.value,
                key_width, pinky_stretch),
        key_width,
        key_width,
        reduced_index_width,  # H-, R-
        compound_key_size,
        computed(lambda: reduced_key_width.value + key_width.value / 2,
                reduced_key_width, key_width),  # *
    )

    col_widths_right = (
        computed(lambda: reduced_key_width.value + key_width.value / 2,
                reduced_key_width, key_width), # *
        compound_key_size,
        reduced_index_width,  # -F, -R
        key_width,
        key_width,
        computed(lambda: reduced_key_width.value + pinky_stretch.value,
                reduced_key_width, pinky_stretch),  # -T, -S
        compound_key_size,
        reduced_key_width,  # -D, -Z
    )

    vowel_set_widths = (
        reduced_key_width,
        compound_key_size,
        reduced_key_width,
    )

    INITIAL_ROWS_GAP = 2.25

    index_stagger_fac = settings.index_stagger_fac_ref
    middle_stagger_fac = settings.middle_stagger_fac_ref
    ring_stagger_fac = settings.ring_stagger_fac_ref
    pinky_stagger_fac = settings.pinky_stagger_fac_ref

    index_offset = computed(lambda: key_width.value * index_stagger_fac.value,
            key_width, index_stagger_fac)
    middle_offset = computed(lambda: key_width.value * middle_stagger_fac.value,
            key_width, middle_stagger_fac)
    ring_offset = computed(lambda: key_width.value * ring_stagger_fac.value,
            key_width, ring_stagger_fac)
    pinky_offset = computed(lambda: key_width.value * pinky_stagger_fac.value,
            key_width, pinky_stagger_fac)

    col_offsets = (
        pinky_offset,  # S-
        ring_offset,  # T-, K-
        middle_offset,  # P-, W-
        index_offset,  # H-, R-
        index_offset,
        index_offset,
        index_offset,
        index_offset,  # -F, -R
        middle_offset,  # -P, -B
        ring_offset,  # -L, -G
        pinky_offset,  # -T, -S
        pinky_offset,
        pinky_offset, # -D, -Z
    )

    col_offsets_left = (
        pinky_offset,  # S-
        ring_offset,  # T-, K-
        middle_offset,  # P-, W-
        index_offset,  # H-, R-
        index_offset,
        index_offset,
    )

    col_offsets_right = (
        index_offset,
        index_offset,
        index_offset,  # -F, -R
        middle_offset,  # -P, -B
        ring_offset,  # -L, -G
        pinky_offset,  # -T, -S
        pinky_offset,
        pinky_offset, # -D, -Z
    )

    ASTERISK_COLUMN_INDEX = 5


    def build_main_rows_hand_staggered(
        key_widgets: list[KeyWidget],
        keys: tuple[list[str], str, int, str],
        col_widths: tuple[Ref[float]],
        col_offsets: tuple[Ref[float]],
    ) -> QLayout:
        # Parameter defaults on inner functions are used to create closures

        layout = QHBoxLayout()
        for column, col_width_cm, col_offset_cm in zip(keys, col_widths, col_offsets):
            column_layout = QVBoxLayout()
            column_layout.addStretch(1)

            row_pos = 0

            for values, label, *rest in column:
                row_span: int = rest[0] if len(rest) > 0 else 1
                row_heights_cm = row_heights[row_pos:row_pos + row_span]


                key_widget = KeyWidget(values, label, keyboard_widget)
                key_widgets.append(key_widget)

                if len(rest) > 1:
                    num_bar_label: str = rest[1]
                    keyboard_widget.num_bar_pressed_change.connect(key_widget.num_bar_pressed_handler(label, num_bar_label))


                if row_pos <= _LOW_ROW < row_pos + row_span:
                    def height_boost(col_offset_cm: Ref[float]=col_offset_cm):
                        return col_offset_cm.value / 2
                    row_heights_cm = (*row_heights_cm, computed(height_boost, col_offset_cm))
                        
                @watch_many(dpi.change, col_width_cm.change, *(height.change for height in row_heights_cm), parent=key_widget)
                def resize(
                    key_widget: KeyWidget=key_widget,
                    col_width_cm: Ref[float]=col_width_cm,
                    row_heights_cm: tuple[Ref[float]]=row_heights_cm,
                ):
                    key_widget.setFixedSize(dpi.cm(col_width_cm.value), sum(dpi.cm(height.value) for height in row_heights_cm))


                column_layout.addWidget(key_widget)

                row_pos += row_span


            column_layout.addSpacerItem(column_spacer := QSpacerItem(0, 0))

            @watch_many(dpi.change, col_offset_cm.change, parent=column_layout)
            def resize_column_spacing(
                column_spacer: QSpacerItem=column_spacer,
                col_offset_cm: Ref[float]=col_offset_cm,
            ):
                column_spacer.changeSize(0, dpi.cm(col_offset_cm.value / 2))

        
            layout.addLayout(column_layout)
            layout.setSizeConstraint(QLayout.SetFixedSize)
            
        layout.setSpacing(0)

        return layout


    def build_main_rows_hand_container(
        key_widgets: list[KeyWidget],
        keys: tuple[list[str], str, int, str],
        col_widths: tuple[Ref[float]],
        col_offsets: tuple[float],
        angle: float,
    ) -> RotatableKeyContainer:
        scene = QGraphicsScene(keyboard_widget)

        widget = QWidget()
        widget.setStyleSheet(KEY_STYLESHEET)
        widget.setAttribute(Qt.WA_TranslucentBackground) # Gives this container a transparent background
        widget.setLayout(build_main_rows_hand_staggered(key_widgets, keys, col_widths, col_offsets))
        proxy = scene.addWidget(widget)

        proxy.setRotation(angle)

        return RotatableKeyContainer(widget, proxy, scene, keyboard_widget)


    def build_main_rows_layout_staggered(key_widgets: list[KeyWidget]) -> QLayout:
        layout = QHBoxLayout()
        layout.setSpacing(0)

        layout.addWidget(build_main_rows_hand_container(key_widgets, _MAIN_ROWS_KEYS_LEFT, col_widths_left, col_offsets_left, 10))
        layout.addStretch(1)
        layout.addWidget(build_main_rows_hand_container(key_widgets, _MAIN_ROWS_KEYS_RIGHT, col_widths_right, col_offsets_right, -10))

        return layout


    def build_main_rows_layout_grid(key_widgets: list[KeyWidget]) -> QLayout:
        layout = QGridLayout()
        for values, label, grid_position, *rest in _MAIN_ROWS_KEYS_GRID:
            key_widget = KeyWidget(values, label, keyboard_widget)
            key_widgets.append(key_widget)
            
            if len(rest) > 0:
                num_bar_label: str = rest[0]
                keyboard_widget.num_bar_pressed_change.connect(key_widget.num_bar_pressed_handler(label, num_bar_label))

            layout.addWidget(key_widget, *grid_position)

        for i, size_cm in enumerate(row_heights):
            layout.setRowMinimumHeight(i, dpi.cm(size_cm.value))
            layout.setRowStretch(i, 0)

        for i, size_cm in enumerate(col_widths):
            layout.setColumnMinimumWidth(i, dpi.cm(size_cm.value))
            layout.setColumnStretch(i, 0)


        layout.setColumnStretch(ASTERISK_COLUMN_INDEX, 1)
        @watch(dpi.change, parent=layout)
        def resize_asterisk_column():
            QTimer.singleShot(0, lambda: layout.setColumnMinimumWidth(ASTERISK_COLUMN_INDEX, 0))


        @on_many(dpi.change, *(height.change for height in row_heights), *(width.change for width in col_widths), parent=layout)
        def resize_columns():
            for i, size_cm in enumerate(row_heights):
                layout.setRowMinimumHeight(i, dpi.cm(size_cm.value))

            for i, size_cm in enumerate(col_widths):
                if i == ASTERISK_COLUMN_INDEX: continue
                layout.setColumnMinimumWidth(i, dpi.cm(size_cm.value))


        layout.setSpacing(0)


        return layout


    def build_vowel_row_layout(key_widgets: list[KeyWidget]) -> QLayout:
        # Parameter defaults on inner functions are used to create closures
        
        layout = QHBoxLayout()
        layout.setSpacing(0)

        def add_vowel_set(vowel_key_descriptors):
            for (values, label, *rest), width in zip(vowel_key_descriptors, vowel_set_widths):
                key_widget = KeyWidget(values, label, keyboard_widget)
                key_widgets.append(key_widget)
            
                if len(rest) > 0:
                    num_bar_label: str = rest[0]
                    keyboard_widget.num_bar_pressed_change.connect(key_widget.num_bar_pressed_handler(label, num_bar_label))


                @watch_many(dpi.change, width.change, key_height.change, parent=key_widget)
                def resize(
                    key_widget: KeyWidget=key_widget,
                    width: Ref[float]=width,
                ):
                    key_widget.setFixedSize(dpi.cm(width.value), dpi.cm(key_height.value))


                layout.addWidget(key_widget)

        
        layout.addSpacerItem(left_spacer := QSpacerItem(0, 0))
        add_vowel_set(_VOWEL_ROW_KEYS_LEFT)
        layout.addStretch(1)
        add_vowel_set(_VOWEL_ROW_KEYS_RIGHT)
        layout.addSpacerItem(right_spacer := QSpacerItem(0, 0))

        @watch_many(dpi.change, key_width.change, pinky_stretch.change, index_stretch.change, vowel_set_offset.change,
                parent=layout)
        def resize_spacing():
            left_bank_width = dpi.cm(key_width.value) * 4 + dpi.cm(pinky_stretch.value) + dpi.cm(index_stretch.value)
            right_bank_width = left_bank_width + dpi.cm(key_width.value)

            left_spacer.changeSize(left_bank_width - dpi.cm(key_width.value) - dpi.cm(vowel_set_offset.value), 0)
            right_spacer.changeSize(right_bank_width - dpi.cm(key_width.value) - dpi.cm(vowel_set_offset.value), 0)

        @on_many(key_width.change, vowel_set_offset.change, parent=layout)
        def invalidate_layout():
            layout.invalidate()


        return layout


    def build_keyboard_layout(
        build_main_rows: Callable[[KeyboardWidget, list[KeyWidget]], QLayout],
        build_vowel_row: Callable[[KeyboardWidget, list[KeyWidget]], QLayout],
        key_widgets: list[KeyWidget],
    ) -> QLayout:
        """Generates a keyboard layout.
        
            :param key_widgets: A list that will be populated with the `KeyWidget`s.
        """

        # QVBoxLayout has an odd side effect when window is resized to a large enough height; the main rows layout would
        # start to grow along with the spacer item
        layout = QGridLayout()

        layout.addLayout(build_main_rows(key_widgets), 0, 0)

        layout.setRowStretch(1, 1)
        
        @watch(dpi.change)
        def resize_row_spacer():
            layout.setRowMinimumHeight(1, dpi.cm(INITIAL_ROWS_GAP))
            QTimer.singleShot(0, lambda: layout.setRowMinimumHeight(1, 0))

        layout.addLayout(build_vowel_row(key_widgets), 2, 0)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        return layout


    return {
        KeyLayout.STAGGERED: partial(build_keyboard_layout, build_main_rows_layout_staggered, build_vowel_row_layout),
        KeyLayout.GRID: partial(build_keyboard_layout, build_main_rows_layout_grid, build_vowel_row_layout),
    }

#endregion