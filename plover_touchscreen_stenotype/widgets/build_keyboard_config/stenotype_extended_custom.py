from math import sin, cos, radians
from typing import Callable

from ...settings import Settings
from ...lib.reactivity import Ref, computed
from ...lib.types import LayoutDescriptor, KeyColumnsTuple, KeyGridTuple

def build_layout_descriptor(settings: Settings) -> LayoutDescriptor:
    #region Key layouts

    TOP_ROW = 0
    LOW_ROW = 2
    LOW_COMPOUND_ROW = 1

    # [keys], label, rowSpan?, numberLabel?
    MAIN_ROWS_KEYS_STAGGERED_LEFT: KeyColumnsTuple = (
        (
            (["^-"], "^"), # ∧
            (["^-", "+-"], ""),
            (["+-"], "+"),
        ), (
            (["^-", "S-"], ""),
            (["^-", "+-", "S-"], ""),
            (["+-", "S-"], ""),
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
            (["H-", "&-"], ""),
            (["H-", "R-", "&-"], ""),
            (["R-", "&-"], ""),
        # ), (
        #     (["&-"], "&&", 3), # ＋
        # ), (
        #     (["&-", ".-"], "&&&&", 3),
        # ),
        ), (
            (["&-"], "&&", 3), # ＋
        ),
    )

    MAIN_ROWS_KEYS_STAGGERED_RIGHT: KeyColumnsTuple = (
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
    MAIN_ROWS_KEYS_GRID: KeyGridTuple = (
        (["^-"], "^", (TOP_ROW, 0)),
        (["+-"], "+", (LOW_ROW, 0)),
        (["^-", "S-"], "", (TOP_ROW, 1)),
        (["+-", "S-"], "", (LOW_ROW, 1)),
        (["S-"], "S", (TOP_ROW, 2, 3, 1), "1"),
        (["T-"], "T", (TOP_ROW, 3), "2"),
        (["K-"], "K", (LOW_ROW, 3)),
        (["P-"], "P", (TOP_ROW, 4), "3"),
        (["W-"], "W", (LOW_ROW, 4)),
        (["H-"], "H", (TOP_ROW, 5), "4"),
        (["R-"], "R", (LOW_ROW, 5)),
        (["H-", "*"], "", (TOP_ROW, 6)),
        (["R-", "*"], "", (LOW_ROW, 6)),
        (["*"], "🞱", (TOP_ROW, 7, 3, 1)),
        (["*", "-F"], "", (TOP_ROW, 8)),
        (["*", "-R"], "", (LOW_ROW, 8)),
        (["-F"], "F", (TOP_ROW, 9), "6"),
        (["-R"], "R", (LOW_ROW, 9)),
        (["-P"], "P", (TOP_ROW, 10), "7"),
        (["-B"], "B", (LOW_ROW, 10)),
        (["-L"], "L", (TOP_ROW, 11), "8"),
        (["-G"], "G", (LOW_ROW, 11)),
        (["-T"], "T", (TOP_ROW, 12), "9"),
        (["-S"], "S", (LOW_ROW, 12)),
        (["-T", "-D"], "", (TOP_ROW, 13)),
        (["-S", "-Z"], "", (LOW_ROW, 13)),
        (["-D"], "D", (TOP_ROW, 14)),
        (["-Z"], "Z", (LOW_ROW, 14)),

        (["^-", "+-"], "", (LOW_COMPOUND_ROW, 0)),
        (["^-", "+-", "S-"], "", (LOW_COMPOUND_ROW, 1)),
        (["T-", "K-"], "", (LOW_COMPOUND_ROW, 3)),
        (["P-", "W-"], "", (LOW_COMPOUND_ROW, 4)),
        (["H-", "R-"], "", (LOW_COMPOUND_ROW, 5)),
        (["H-", "R-", "*"], "", (LOW_COMPOUND_ROW, 6)),
        (["*", "-R", "-F"], "", (LOW_COMPOUND_ROW, 8)),
        (["-F", "-R"], "", (LOW_COMPOUND_ROW, 9)),
        (["-P", "-B"], "", (LOW_COMPOUND_ROW, 10)),
        (["-L", "-G"], "", (LOW_COMPOUND_ROW, 11)),
        (["-T", "-S"], "", (LOW_COMPOUND_ROW, 12)),
        (["-T", "-S", "-D", "-Z"], "", (LOW_COMPOUND_ROW, 13)),
        (["-D", "-Z"], "", (LOW_COMPOUND_ROW, 14)),
    )

    VOWEL_ROW_KEYS_LEFT: KeyGridTuple = (
        (["A-"], "A", (0, 0), "5"),
        (["A-", "O-"], "", (0, 1)),
        (["O-"], "O", (0, 2), "0"),
        
        (["#", "A-"], "", (1, 0)),
        (["#", "A-", "O-"], "", (1, 1)),
        (["#", "O-"], "", (1, 2)),

        (["#"], "#", (2, 0, 1, 3)),
    )

    VOWEL_ROW_KEYS_RIGHT: KeyGridTuple = (
        (["-E"], "E", (0, 0)),
        (["-E", "-U"], "", (0, 1)),
        (["-U"], "U", (0, 2)),
        
        (["_", "-E"], "", (1, 0)),
        (["_", "-E", "-U"], "", (1, 1)),
        (["_", "-U"], "", (1, 2)),

        (["_"], "_", (2, 0, 1, 3)),
    )

    #endregion

    #region Size values

    # in centimeters
    key_width = settings.key_width_ref
    key_height = settings.key_height_ref
    compound_key_size = settings.compound_key_size_ref


    """Computes the size of a key that has half of a compound key cutting into it"""
    reduced_size: Callable[[Ref[float], Ref[float]], Ref[float]] = lambda key_size_ref, compound_size_ref: (
            computed(lambda: key_size_ref.value - compound_size_ref.value / 2,
                    key_size_ref, compound_size_ref)
    )

    reduced_key_width = reduced_size(key_width, compound_key_size)
    reduced_key_height = reduced_size(key_height, compound_key_size)

    """ key_height_num_bar = computed(lambda: key_height.value / 2,
            key_height) """

    index_stretch = settings.index_stretch_ref
    pinky_stretch = settings.pinky_stretch_ref

    vowel_set_offset_fac = settings.vowel_set_offset_fac_ref
    vowel_set_offset = computed(lambda: key_width.value * vowel_set_offset_fac.value,
            key_width, vowel_set_offset_fac)

    """Default row heights for every main rows column"""
    row_heights = (
        reduced_key_height,  # top row
        compound_key_size,
        reduced_key_height,  # bottom row
    )


    # Row heights for specific columns in staggered mode

    compound_height_small = computed(lambda: compound_key_size.value * 0.75,
            compound_key_size)
    reduced_height_small = reduced_size(key_height, compound_height_small)

    row_heights_small = (
        reduced_height_small,
        compound_height_small,
        reduced_height_small,
    )


    row_heights_staggered_left = (
        *(row_heights_small,) * 3,
        *(row_heights,) * 2,
        *(row_heights_small,) * 4,
    )

    row_heights_staggered_right = (
        *(row_heights_small,) * 3,
        *(row_heights,) * 2,
        *(row_heights_small,) * 3,
    )


    index_compound_width = computed(lambda: compound_key_size.value * 0.6,
            compound_key_size)    
    base_index_width = computed(lambda: key_width.value + index_stretch.value,
            key_width, index_stretch)
    reduced_index_width = reduced_size(base_index_width, index_compound_width)


    END_COLUMN_WIDTH_BOOST = 0.4

    end_column_compound_width = computed(lambda: compound_key_size.value * 0.875,
            compound_key_size)
    
    end_column_width = reduced_size(
        computed(lambda: key_width.value + END_COLUMN_WIDTH_BOOST,
                key_width),
        end_column_compound_width,
    )
    inner_end_column_width = reduced_size(
        computed(lambda: key_width.value + pinky_stretch.value,
                key_width, pinky_stretch),
        end_column_compound_width,
    )

    center_key_width = computed(lambda: reduced_key_width.value + key_width.value / 2,
                reduced_key_width, key_width)

    col_widths_staggered_left = (
        end_column_width,
        end_column_compound_width,
        inner_end_column_width,
        key_width,
        key_width,
        reduced_index_width,  # H-, R-
        index_compound_width,
        center_key_width, # &
        # computed(lambda: (key_width.value * 1.5 - compound_key_size.value / 2) / 2,
        #         key_width, compound_key_size),  # +
        # computed(lambda: (key_width.value * 1.5 - compound_key_size.value / 2) / 2,
        #         key_width, compound_key_size),  # .
    )

    col_widths_staggered_right = (
        center_key_width, # *
        index_compound_width,
        reduced_index_width,  # -F, -R
        key_width,
        key_width,
        inner_end_column_width,  # -T, -S
        end_column_compound_width,
        end_column_width,  # -D, -Z
    )

    VOWEL_KEY_WIDTH_BOOST = 0.25

    vowel_set_widths = (
        computed(lambda: reduced_key_width.value + VOWEL_KEY_WIDTH_BOOST,
                reduced_key_width),
        compound_key_size,
        computed(lambda: reduced_key_width.value + VOWEL_KEY_WIDTH_BOOST,
                reduced_key_width),
    )

    vowel_compound_key_height = index_compound_width

    vowel_set_heights = (
        reduced_size(key_height, vowel_compound_key_height),
        vowel_compound_key_height,
        reduced_size(computed(lambda: key_height.value * 0.75, key_height), vowel_compound_key_height),
    )

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


    col_offsets_staggered_left = (
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

    col_offsets_staggered_right = (
        index_offset,
        index_offset,
        index_offset,  # -F, -R
        middle_offset,  # -P, -B
        ring_offset,  # -L, -G
        pinky_offset,  # -T, -S
        pinky_offset,
        pinky_offset, # -D, -Z
    )

    col_widths_grid = (
        *col_widths_staggered_left[:-1],
        computed(lambda: reduced_key_width.value * 2 + key_width.value * 2.5,
                reduced_key_width, key_width),  # *
        *col_widths_staggered_right[1:],
    )

    #endregion


    return LayoutDescriptor(
        MAIN_ROWS_STAGGERED_LEFT=MAIN_ROWS_KEYS_STAGGERED_LEFT,
        MAIN_ROWS_STAGGERED_RIGHT=MAIN_ROWS_KEYS_STAGGERED_RIGHT,
        col_widths_staggered_left=col_widths_staggered_left,
        col_widths_staggered_right=col_widths_staggered_right,
        row_heights_staggered_left=row_heights_staggered_left,
        row_heights_staggered_right=row_heights_staggered_right,
        col_offsets_staggered_left=col_offsets_staggered_left,
        col_offsets_staggered_right=col_offsets_staggered_right,
        TALLEST_COLUMN_INDEX_LEFT=3,
        TALLEST_COLUMN_INDEX_RIGHT=3,

        N_INDEX_COLS_LEFT=5,
        N_INDEX_COLS_RIGHT=5,

        MAIN_ROWS_GRID=MAIN_ROWS_KEYS_GRID,
        row_heights_grid=row_heights,
        col_widths_grid=col_widths_grid,
        ASTERISK_COLUMN_INDEX_GRID=7,

        VOWEL_ROW_KEYS_LEFT=VOWEL_ROW_KEYS_LEFT,
        VOWEL_ROW_KEYS_RIGHT=VOWEL_ROW_KEYS_RIGHT,
        vowel_set_widths=vowel_set_widths,
        vowel_set_heights=vowel_set_heights,
        vowel_set_offset=vowel_set_offset,

        LOW_ROW=LOW_ROW,
    )