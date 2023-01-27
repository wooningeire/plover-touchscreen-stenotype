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
    QWidget,
    QSizePolicy,
    QWidgetItem,
    QLayoutItem,
)

from math import sin, cos, radians
from functools import partial
from typing import TYPE_CHECKING, Callable, Iterable
if TYPE_CHECKING:
    from .KeyboardWidget import KeyboardWidget
else:
    KeyboardWidget = object

from .KeyWidget import KeyWidget
from .RotatableKeyContainer import RotatableKeyContainer
from ..settings import Settings, KeyLayout
from ..util import UseDpi, Ref, computed, computed_on_signal, on, on_many, watch, watch_many


_TOP_ROW = 0
_LOW_ROW = 2
_TOP_COMPOUND_ROW = -1
_LOW_COMPOUND_ROW = 1

# [keys], label, rowSpan?, numberLabel?
_MAIN_ROWS_KEYS_STAGGERED_LEFT = (
    (
        (["#"], "#"),
        (["#", "^-"], ""),
        (["^-"], "^"), # ∧
    ), (
        (["#", "S-"], ""),
        (["#", "^-", "S-"], ""),
        (["^-", "S-"], ""),
    ), (
        (["S-"], "S", 3, "1"),
    ), (
        (["T-"], "T", 1, "2"),
        (["T-", "K-"], ""),
        (["K-"], "K"),
    ), (
        (["P-"], "P", 1, "3"),
        (["P-", "W-"], ""),
        (["W-"], "W"),
    ), (
        (["H-"], "H", 1, "4"),
        (["H-", "R-"], ""),
        (["R-"], "R"),
    ), (
        (["H-", "+-"], ""),
        (["H-", "R-", "+-"], ""),
        (["R-", "+-"], ""),
    ), (
        (["+-"], "+", 3), # ＋
    ), (
        (["+-", ".-"], "++", 3),
    ),
)

_MAIN_ROWS_KEYS_STAGGERED_RIGHT = (
    (
        (["*"], "🞱", 3),
    ), (
        (["*", "-F"], ""),
        (["*", "-F", "-R"], ""),
        (["*", "-R"], ""),
    ), (
        (["-F"], "F", 1, "6"),
        (["-F", "-R"], ""),
        (["-R"], "R"),
    ), (
        (["-P"], "P", 1, "7"),
        (["-P", "-B"], ""),
        (["-B"], "B"),
    ), (
        (["-L"], "L", 1, "8"),
        (["-L", "-G"], ""),
        (["-G"], "G"),
    ), (
        (["-T"], "T", 1, "9"),
        (["-T", "-S"], ""),
        (["-S"], "S"),
    ), (
        (["-T", "-D"], ""),
        (["-T", "-S", "-D", "-Z"], ""),
        (["-S", "-Z"], ""),
    ), (
        (["-D"], "D"),
        (["-D", "-Z"], ""),
        (["-Z"], "Z"),
    ),
)

# [keys], label, (row, column, rowSpan?, columnSpan?), numberLabel?
_MAIN_ROWS_KEYS_GRID = (
    (["#"], "#", (_TOP_ROW, 0)),
    (["S-"], "S", (_LOW_ROW, 0), "1"),
    (["T-"], "T", (_TOP_ROW, 1), "2"),
    (["K-"], "K", (_LOW_ROW, 1)),
    (["P-"], "P", (_TOP_ROW, 2), "3"),
    (["W-"], "W", (_LOW_ROW, 2)),
    (["H-"], "H", (_TOP_ROW, 3), "4"),
    (["R-"], "R", (_LOW_ROW, 3)),
    (["H-", "*"], "", (_TOP_ROW, 4)),
    (["R-", "*"], "", (_LOW_ROW, 4)),
    (["*"], "🞱", (_TOP_ROW, 5, 3, 1)),
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

    (["#", "S-"], "", (_LOW_COMPOUND_ROW, 0)),
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

    END_COLUMN_WIDTH_BOOST = 0.4

    col_widths_staggered_left = (
        computed(lambda: reduced_key_width.value + END_COLUMN_WIDTH_BOOST,
                reduced_key_width),
        compound_key_size,
        computed(lambda: reduced_key_width.value + pinky_stretch.value,
                reduced_key_width, pinky_stretch),
        key_width,
        key_width,
        reduced_index_width,  # H-, R-
        computed(lambda: compound_key_size.value * 5/6,
                compound_key_size),
        computed(lambda: (key_width.value * 1.5 - compound_key_size.value / 2) / 2,
                key_width, compound_key_size),  # +
        computed(lambda: (key_width.value * 1.5 - compound_key_size.value / 2) / 2,
                key_width, compound_key_size),  # .
    )

    col_widths_staggered_right = (
        computed(lambda: reduced_key_width.value + key_width.value / 2,
                reduced_key_width, key_width), # *
        computed(lambda: compound_key_size.value * 5/6,
                compound_key_size),
        reduced_index_width,  # -F, -R
        key_width,
        key_width,
        computed(lambda: reduced_key_width.value + pinky_stretch.value,
                reduced_key_width, pinky_stretch),  # -T, -S
        compound_key_size,
        computed(lambda: reduced_key_width.value + END_COLUMN_WIDTH_BOOST,
                reduced_key_width),  # -D, -Z
    )

    VOWEL_KEY_WIDTH_BOOST = 0.25

    vowel_set_widths = (
        computed(lambda: reduced_key_width.value + VOWEL_KEY_WIDTH_BOOST,
                reduced_key_width),
        compound_key_size,
        computed(lambda: reduced_key_width.value + VOWEL_KEY_WIDTH_BOOST,
                reduced_key_width),
    )

    INITIAL_ROWS_GAP_HEIGHT = 2.25

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
        pinky_offset,
        pinky_offset,
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

    """
    col_offsets = (
        0,  # S-
        key_width.value * 0.375,  # T-, K-
        key_width.value * 0.6,  # P-, W-
        0,  # H-, R-
        0,
        0,
        0,
        0,  # -F, -R
        key_width.value * 0.6,  # -P, -B
        key_width.value * 0.375,  # -L, -G
        0,  # -T, -S
        0,
        0,  # -D, -Z
    )
    """


    col_offsets_left = (
        pinky_offset,
        pinky_offset,
        pinky_offset,  # S-
        ring_offset,  # T-, K-
        middle_offset,  # P-, W-
        index_offset,  # H-, R-
        index_offset,
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

    # in degrees
    main_rows_angle = settings.main_rows_angle_ref
    vowel_rows_angle = settings.vowel_rows_angle_ref


    ASTERISK_COLUMN_INDEX = 5


    TALLEST_COLUMN_INDEX_LEFT = 4
    TALLEST_COLUMN_INDEX_RIGHT = 4


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
            column_layout.setSizeConstraint(QLayout.SetFixedSize)
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
        layout.setContentsMargins(0, 0, 0, 0)

        return layout


    def build_main_rows_hand_container(
        key_widgets: list[KeyWidget],
        keys: tuple[list[str], str, int, str],
        col_widths: tuple[Ref[float]],
        col_offsets: tuple[float],
        angle: Ref[float],
        align_left: bool,
    ) -> QLayout:
        layout = build_main_rows_hand_staggered(key_widgets, keys, col_widths, col_offsets)
        container = RotatableKeyContainer.of_layout(layout, align_left, angle.value, keyboard_widget)

        @on(angle.change)
        def update_vowel_angle(value: float):
            container.angle = angle.value


        offset_layout = QVBoxLayout()
        offset_layout.addStretch(1) # Forces containers to be aligned to bottom

        # Allows height to be subtracted from container without being consumed by the stretch spacer
        direct_layout = QVBoxLayout()
        direct_layout.addSpacerItem(offset_spacer := QSpacerItem(0, 0))


        @watch_many(dpi.change, key_width.change, key_height.change, compound_key_size.change,
                pinky_stretch.change, index_stretch.change, index_stagger_fac.change,
                middle_stagger_fac.change, ring_stagger_fac.change, pinky_stagger_fac.change,
                angle.change, parent=container)
        def set_proxy_transform_and_container_size():
            # Removes the additional height caused by the rotation when the layout and key widget corners do not match
            if align_left:
                widths = col_widths_staggered_right[-TALLEST_COLUMN_INDEX_RIGHT:]
            else:
                widths = col_widths_staggered_left[:TALLEST_COLUMN_INDEX_LEFT]

            radius = sum(dpi.cm(width.value) for width in widths)
            offset = radius * -sin(radians(abs(angle.value)))

            offset_spacer.changeSize(0, round(offset))

            container.update_size()

        direct_layout.addWidget(container)

        offset_layout.addLayout(direct_layout)

        return offset_layout


    def build_main_rows_layout_staggered(key_widgets: list[KeyWidget]) -> QLayout:
        layout = QHBoxLayout()
        layout.setSpacing(0)

        layout.addLayout(build_main_rows_hand_container(
                key_widgets, _MAIN_ROWS_KEYS_STAGGERED_LEFT, col_widths_staggered_left, col_offsets_left,
                main_rows_angle, False))
        layout.addStretch(1)
        layout.addLayout(build_main_rows_hand_container(
                key_widgets, _MAIN_ROWS_KEYS_STAGGERED_RIGHT, col_widths_staggered_right, col_offsets_right,
                computed(lambda: -main_rows_angle.value, main_rows_angle), True))

        return layout

        """ container_layout = QVBoxLayout()
        container_layout.addLayout(layout)
        container_layout.addStretch(1)

        return container_layout """


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


    def build_vowel_set_layout(vowel_key_descriptors: tuple[Iterable[str], str, str], key_widgets: list[KeyWidget]):
        # Parameter defaults on inner functions are used to create closures

        set_layout = QHBoxLayout()
        set_layout.setSpacing(0)
        set_layout.setContentsMargins(0, 0, 0, 0)
        set_layout.setSizeConstraint(QLayout.SetFixedSize)

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


            set_layout.addWidget(key_widget)

        return set_layout

    def build_vowel_row_containing_sets(left_set: QLayoutItem, right_set: QLayoutItem) -> QLayout:
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addSpacerItem(left_spacer := QSpacerItem(0, 0))
        layout.addItem(left_set)
        layout.addStretch(1)
        layout.addItem(right_set)
        layout.addSpacerItem(right_spacer := QSpacerItem(0, 0))

        @watch_many(dpi.change, key_width.change, pinky_stretch.change, index_stretch.change, vowel_set_offset.change,
                main_rows_angle.change, *(height.change for height in row_heights), parent=layout)
        def resize_spacing():
            left_bank_width = (dpi.cm(key_width.value) * 5 + dpi.cm(pinky_stretch.value) + dpi.cm(index_stretch.value)) * cos(radians(main_rows_angle.value))
            right_bank_width = left_bank_width

            offset = (dpi.cm(key_width.value) + dpi.cm(vowel_set_offset.value)) * cos(radians(main_rows_angle.value))

            left_bank_spacing = left_bank_width - offset
            right_bank_spacing = right_bank_width - offset

            left_spacer.changeSize(left_bank_spacing, 0)
            right_spacer.changeSize(right_bank_spacing, 0)

        @on_many(key_width.change, vowel_set_offset.change, parent=layout)
        def invalidate_layout():
            layout.invalidate()

        return layout


    def build_vowel_row_layout_staggered(key_widgets: list[KeyWidget]) -> QLayout:
        left_set_layout = build_vowel_set_layout(_VOWEL_ROW_KEYS_LEFT, key_widgets)
        left_container = RotatableKeyContainer.of_layout(left_set_layout, False, vowel_rows_angle.value, keyboard_widget)
        
        right_set_layout = build_vowel_set_layout(_VOWEL_ROW_KEYS_RIGHT, key_widgets)
        right_container = RotatableKeyContainer.of_layout(right_set_layout, True, -vowel_rows_angle.value, keyboard_widget)

        @on(vowel_rows_angle.change)
        def change_vowel_angle(value: float):
            left_container.angle = value
            right_container.angle = -value

        layout = build_vowel_row_containing_sets(QWidgetItem(left_container), QWidgetItem(right_container))


        @watch_many(dpi.change, key_width.change, key_height.change, compound_key_size.change,
                pinky_stretch.change, index_stretch.change,
                parent=layout)
        def update_sizes():
            left_container.update_size()
            right_container.update_size()
        
        return layout


    def build_vowel_row_layout_grid(key_widgets: list[KeyWidget]) -> QLayout:
        return build_vowel_row_containing_sets(
            build_vowel_set_layout(_VOWEL_ROW_KEYS_LEFT, key_widgets),
            build_vowel_set_layout(_VOWEL_ROW_KEYS_RIGHT, key_widgets),
        )


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
        def resize_spacer_row():
            layout.setRowMinimumHeight(1, dpi.cm(INITIAL_ROWS_GAP_HEIGHT))
            # Allow negative stretch so the other grid rows can overlap
            QTimer.singleShot(0, lambda: layout.setRowMinimumHeight(1, -16777216))

        layout.addLayout(build_vowel_row(key_widgets), 2, 0)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        return layout


    return {
        KeyLayout.STAGGERED: partial(build_keyboard_layout, build_main_rows_layout_staggered, build_vowel_row_layout_staggered),
        KeyLayout.GRID: partial(build_keyboard_layout, build_main_rows_layout_grid, build_vowel_row_layout_grid),
    }

#endregion