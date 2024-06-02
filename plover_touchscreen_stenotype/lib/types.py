from dataclasses import dataclass

from .reactivity import Ref

KeyColumnsTuple = tuple[
    tuple[
        tuple[list[str], str, "int | None", "str | None"]
    ]
]
KeyGridTuple = tuple[
    tuple[
        list[str],
        str,
        "tuple[int, int] | tuple[int, int, int, int]",
        "str | None",
    ]
]
SizeTuple = tuple[Ref[float]]

@dataclass
class LayoutDescriptor:
    MAIN_ROWS_STAGGERED_LEFT: KeyColumnsTuple
    MAIN_ROWS_STAGGERED_RIGHT: KeyColumnsTuple
    col_widths_staggered_left: SizeTuple
    col_widths_staggered_right: SizeTuple
    col_offsets_staggered_left: SizeTuple
    col_offsets_staggered_right: SizeTuple
    row_heights_staggered_left: SizeTuple
    row_heights_staggered_right: SizeTuple
    TALLEST_COLUMN_INDEX_LEFT: float
    TALLEST_COLUMN_INDEX_RIGHT: float

    N_INDEX_COLS_LEFT: float
    N_INDEX_COLS_RIGHT: float

    VOWEL_ROW_KEYS_LEFT: KeyGridTuple
    VOWEL_ROW_KEYS_RIGHT: KeyGridTuple
    vowel_set_widths: SizeTuple
    vowel_set_heights: SizeTuple
    vowel_set_offset: Ref[float]

    LOW_ROW: float