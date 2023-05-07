from PyQt5.QtCore import (
    QTimer,
)
from PyQt5.QtWidgets import (
    QLayout,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSpacerItem,
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
from ..util import UseDpi, Ref, computed, on, on_many, watch, watch_many


#region Exports

def use_build_keyboard(settings: Settings, keyboard_widget: KeyboardWidget, dpi: UseDpi):
    from .build_keyboard_config.english_stenotype import build_layout_descriptor
    layout_descriptor = build_layout_descriptor(settings)

    MAIN_ROWS_STAGGERED_LEFT = layout_descriptor.MAIN_ROWS_STAGGERED_LEFT
    MAIN_ROWS_STAGGERED_RIGHT = layout_descriptor.MAIN_ROWS_STAGGERED_RIGHT
    col_widths_staggered_left = layout_descriptor.col_widths_staggered_left
    col_widths_staggered_right = layout_descriptor.col_widths_staggered_right
    row_heights_staggered_left = layout_descriptor.row_heights_staggered_left
    row_heights_staggered_right = layout_descriptor.row_heights_staggered_right
    col_offsets_staggered_left = layout_descriptor.col_offsets_staggered_left
    col_offsets_staggered_right = layout_descriptor.col_offsets_staggered_right
    TALLEST_COLUMN_INDEX_LEFT = layout_descriptor.TALLEST_COLUMN_INDEX_LEFT
    TALLEST_COLUMN_INDEX_RIGHT = layout_descriptor.TALLEST_COLUMN_INDEX_RIGHT

    N_INDEX_COLS_LEFT = layout_descriptor.N_INDEX_COLS_LEFT
    N_INDEX_COLS_RIGHT = layout_descriptor.N_INDEX_COLS_RIGHT

    MAIN_ROWS_GRID = layout_descriptor.MAIN_ROWS_GRID
    row_heights_grid = layout_descriptor.row_heights_grid
    col_widths_grid = layout_descriptor.col_widths_grid
    ASTERISK_COLUMN_INDEX_GRID = layout_descriptor.ASTERISK_COLUMN_INDEX_GRID

    VOWEL_ROW_KEYS_LEFT = layout_descriptor.VOWEL_ROW_KEYS_LEFT
    VOWEL_ROW_KEYS_RIGHT = layout_descriptor.VOWEL_ROW_KEYS_RIGHT
    vowel_set_widths = layout_descriptor.vowel_set_widths
    vowel_set_heights = layout_descriptor.vowel_set_heights
    vowel_set_offset = layout_descriptor.vowel_set_offset
    
    LOW_ROW = layout_descriptor.LOW_ROW

    
    key_width = settings.key_width_ref
    key_height = settings.key_height_ref
    compound_key_size = settings.compound_key_size_ref

    index_stagger_fac = settings.index_stagger_fac_ref
    middle_stagger_fac = settings.middle_stagger_fac_ref
    ring_stagger_fac = settings.ring_stagger_fac_ref
    pinky_stagger_fac = settings.pinky_stagger_fac_ref

    index_stretch = settings.index_stretch_ref
    pinky_stretch = settings.pinky_stretch_ref

    # in degrees
    main_rows_angle = settings.main_rows_angle_ref
    vowel_rows_angle = settings.vowel_rows_angle_ref
    

    INITIAL_ROWS_GAP_HEIGHT = 2.25


    def build_main_rows_hand_staggered(
        key_widgets: list[KeyWidget],
        keys: tuple[list[str], str, int, str],
        col_widths: tuple[Ref[float]],
        col_offsets: tuple[Ref[float]],
        row_heights: tuple[Ref[float]],
    ) -> QLayout:
        # Parameter defaults on inner functions are used to create closures

        layout = QHBoxLayout()
        for column, col_width_cm, col_offset_cm, heights in zip(keys, col_widths, col_offsets, row_heights):
            column_layout = QVBoxLayout()
            column_layout.setSizeConstraint(QLayout.SetFixedSize)
            column_layout.addStretch(1)

            row_pos = 0

            for values, label, *rest in column:
                row_span: int = rest[0] if len(rest) > 0 else 1
                row_heights_cm = heights[row_pos:row_pos + row_span]


                key_widget = KeyWidget(values, label, keyboard_widget)
                key_widgets.append(key_widget)

                if len(rest) > 1:
                    num_bar_label: str = rest[1]
                    keyboard_widget.num_bar_pressed_change.connect(key_widget.num_bar_pressed_handler(label, num_bar_label))


                if row_pos <= LOW_ROW < row_pos + row_span:
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
        row_heights_by_col: tuple[Ref[float]],
        angle: Ref[float],
        align_left: bool,
    ) -> QLayout:
        layout = build_main_rows_hand_staggered(key_widgets, keys, col_widths, col_offsets, row_heights_by_col)
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
                key_widgets, MAIN_ROWS_STAGGERED_LEFT, col_widths_staggered_left, col_offsets_staggered_left,
                row_heights_staggered_left, main_rows_angle, False))
        layout.addStretch(1)
        layout.addLayout(build_main_rows_hand_container(
                key_widgets, MAIN_ROWS_STAGGERED_RIGHT, col_widths_staggered_right, col_offsets_staggered_right,
                row_heights_staggered_right, computed(lambda: -main_rows_angle.value, main_rows_angle), True))

        return layout

        """ container_layout = QVBoxLayout()
        container_layout.addLayout(layout)
        container_layout.addStretch(1)

        return container_layout """


    def build_main_rows_layout_grid(key_widgets: list[KeyWidget]) -> QLayout:
        layout = QGridLayout()
        for values, label, grid_position, *rest in MAIN_ROWS_GRID:
            key_widget = KeyWidget(values, label, keyboard_widget)
            key_widgets.append(key_widget)
            
            if len(rest) > 0:
                num_bar_label: str = rest[0]
                keyboard_widget.num_bar_pressed_change.connect(key_widget.num_bar_pressed_handler(label, num_bar_label))

            layout.addWidget(key_widget, *grid_position)

        for i, size_cm in enumerate(row_heights_grid):
            layout.setRowMinimumHeight(i, dpi.cm(size_cm.value))
            layout.setRowStretch(i, 0)

        for i, size_cm in enumerate(col_widths_grid):
            layout.setColumnMinimumWidth(i, dpi.cm(size_cm.value))
            layout.setColumnStretch(i, 0)


        layout.setColumnStretch(ASTERISK_COLUMN_INDEX_GRID, 1)
        @watch(dpi.change, parent=layout)
        def resize_asterisk_column():
            QTimer.singleShot(0, lambda: layout.setColumnMinimumWidth(ASTERISK_COLUMN_INDEX_GRID, 0))


        @on_many(dpi.change, *(height.change for height in row_heights_grid), *(width.change for width in col_widths_grid), parent=layout)
        def resize_columns():
            for i, size_cm in enumerate(row_heights_grid):
                layout.setRowMinimumHeight(i, dpi.cm(size_cm.value))

            for i, size_cm in enumerate(col_widths_grid):
                if i == ASTERISK_COLUMN_INDEX_GRID: continue
                layout.setColumnMinimumWidth(i, dpi.cm(size_cm.value))


        layout.setSpacing(0)


        return layout


    def build_vowel_set_layout(vowel_key_descriptors: tuple[Iterable[str], str, tuple[int], str], key_widgets: list[KeyWidget]):
        # Parameter defaults on inner functions are used to create closures

        set_layout = QGridLayout()
        set_layout.setSpacing(0)
        set_layout.setContentsMargins(0, 0, 0, 0)
        set_layout.setSizeConstraint(QLayout.SetFixedSize)

        for values, label, grid_position, *rest in vowel_key_descriptors:
            key_widget = KeyWidget(values, label, keyboard_widget)
            key_widgets.append(key_widget)


            if len(grid_position) == 4:
                row_start, col_start, row_span, col_span = grid_position
            elif len(grid_position) == 2:
                row_start, col_start, row_span, col_span = (*grid_position, 1, 1)
            else:
                raise Exception
            
            widths = vowel_set_widths[col_start:col_start + col_span]
            heights = vowel_set_heights[row_start:row_start + row_span]

            if len(rest) > 0:
                num_bar_label: str = rest[0]
                keyboard_widget.num_bar_pressed_change.connect(key_widget.num_bar_pressed_handler(label, num_bar_label))


            @watch_many(dpi.change, *(width.change for width in widths), *(height.change for height in heights), parent=key_widget)
            def resize(
                key_widget: KeyWidget=key_widget,
                widths: tuple[Ref[float]]=widths,
                heights: tuple[Ref[float]]=heights,
            ):
                key_widget.setFixedSize(
                    sum(dpi.cm(width_cm.value) for width_cm in widths),
                    sum(dpi.cm(height_cm.value) for height_cm in heights),
                )


            set_layout.addWidget(key_widget, *grid_position)

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
                main_rows_angle.change, *(height.change for height in row_heights_grid), parent=layout)
        def resize_spacing():
            left_bank_width = (
                sum(dpi.cm(col_width.value) for col_width in col_widths_staggered_left[:N_INDEX_COLS_LEFT])
                + dpi.cm(key_width.value)
                + dpi.cm(pinky_stretch.value)
                + dpi.cm(index_stretch.value)
            ) * cos(radians(main_rows_angle.value))
            right_bank_width = (
                sum(dpi.cm(col_width.value) for col_width in col_widths_staggered_right[-N_INDEX_COLS_RIGHT:])
                + dpi.cm(key_width.value)
                + dpi.cm(pinky_stretch.value)
                + dpi.cm(index_stretch.value)
            ) * cos(radians(main_rows_angle.value))

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
        left_set_layout = build_vowel_set_layout(VOWEL_ROW_KEYS_LEFT, key_widgets)
        left_container = RotatableKeyContainer.of_layout(left_set_layout, False, vowel_rows_angle.value, keyboard_widget)
        
        right_set_layout = build_vowel_set_layout(VOWEL_ROW_KEYS_RIGHT, key_widgets)
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
            build_vowel_set_layout(VOWEL_ROW_KEYS_LEFT, key_widgets),
            build_vowel_set_layout(VOWEL_ROW_KEYS_RIGHT, key_widgets),
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



    right_left_width_diff = computed(lambda:
        (sum(dpi.cm(col_width.value) for col_width in col_widths_staggered_right[-N_INDEX_COLS_RIGHT:]) -
                sum(dpi.cm(col_width.value) for col_width in col_widths_staggered_left[:N_INDEX_COLS_LEFT]))
                * cos(radians(main_rows_angle.value)),
        *(width for width in col_widths_staggered_right[-N_INDEX_COLS_RIGHT:]),
        *(width for width in col_widths_staggered_left[:N_INDEX_COLS_LEFT]),
        main_rows_angle
    )


    return {
        KeyLayout.STAGGERED: partial(build_keyboard_layout, build_main_rows_layout_staggered, build_vowel_row_layout_staggered),
        KeyLayout.GRID: partial(build_keyboard_layout, build_main_rows_layout_grid, build_vowel_row_layout_grid),
    }, right_left_width_diff

#endregion