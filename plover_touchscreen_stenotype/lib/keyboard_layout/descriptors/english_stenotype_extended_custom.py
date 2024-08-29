from math import sin, cos, radians
from typing import Callable, TYPE_CHECKING

from ....settings import Settings
from ...reactivity import Ref, computed
from ..LayoutDescriptor import LayoutDescriptor, Key, KeyGroup, Group, GroupAlignment, GroupOrganization
if TYPE_CHECKING:
    from ....widgets.keyboard.KeyboardWidget import KeyboardWidget
else:
    KeyboardWidget = object

def build_layout_descriptor(settings: Settings, keyboard_widget: KeyboardWidget) -> LayoutDescriptor:
    #region Size values

    # in centimeters
    key_width = settings.key_width_ref
    key_height = settings.key_height_ref
    compound_key_size = settings.compound_key_size_ref


    """Computes the size of a key that has half of a compound key cutting into it"""
    reduced_size: Callable[[Ref[float], Ref[float]], Ref[float]] = lambda key_size_ref, compound_size_ref: key_size_ref - compound_size_ref / 2

    reduced_key_width = reduced_size(key_width, compound_key_size)
    reduced_key_height = reduced_size(key_height, compound_key_size)

    """ key_height_num_bar = computed(lambda: key_height.value / 2,
            key_height) """

    index_stretch = settings.index_stretch_ref
    pinky_stretch = settings.pinky_stretch_ref

    # Row heights for specific columns in staggered mode

    compound_key_height_small = compound_key_size * 0.75
    reduced_key_height_small = reduced_size(key_height, compound_key_height_small)

    
    index_compound_width = compound_key_size * 0.6
    base_index_width = key_width + index_stretch
    reduced_index_width = reduced_size(base_index_width, index_compound_width)
    middle_key_width = reduced_key_width + key_width / 2


    END_COLUMN_WIDTH_BOOST = 0.4

    end_column_compound_width = compound_key_size * 0.875
    
    end_column_width = reduced_size(
        key_width + END_COLUMN_WIDTH_BOOST,
        end_column_compound_width,
    )
    inner_end_column_width = reduced_size(
        key_width + pinky_stretch,
        end_column_compound_width,
    )

    VOWEL_KEY_WIDTH_BOOST = 0.25
    vowel_compound_height = index_compound_width
    vowel_set_heights = (
        reduced_size(key_height, vowel_compound_height),
        vowel_compound_height,
        reduced_size(key_height * 0.75, vowel_compound_height),
    )

    index_offset = key_width * settings.index_stagger_fac_ref
    middle_offset = key_width * settings.middle_stagger_fac_ref
    ring_offset = key_width * settings.ring_stagger_fac_ref
    pinky_offset = key_width * settings.pinky_stagger_fac_ref


    index_group_width = middle_key_width + index_compound_width + reduced_index_width

    #endregion


    return LayoutDescriptor(
        elements=(
            Group(
                alignment=GroupAlignment.TOP_LEFT,

                x=-(index_group_width + settings.bank_spacing_ref / 2),
                y=Ref(0),
                angle=settings.main_rows_angle_ref,

                adaptive_transform=True,

                elements=(
                    Group(
                        alignment=GroupAlignment.TOP_LEFT,
    
                        x=Ref(0),
                        y=Ref(0),
    
                        elements=(
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_RIGHT,
                                organization=GroupOrganization.grid(
                                    row_heights=(
                                        reduced_key_height_small,
                                        compound_key_height_small,
                                        reduced_key_height_small + pinky_offset / 2,
                                    ),
                                    col_widths=(
                                        end_column_width,
                                        end_column_compound_width,
                                        reduced_key_width + pinky_stretch,
                                    ),
                                ),
    
                                x=-2 * settings.key_width_ref,
                                y=-pinky_offset / 2,
    
                                elements=(
                                    Key(steno="&", label="&&", grid_location=(0, 0), center_offset_x=end_column_compound_width / 2, center_offset_y=compound_key_height_small / 2),
                                    Key(steno="&@", grid_location=(1, 0), center_offset_x=end_column_compound_width / 2),
                                    Key(steno="@", label="@", grid_location=(2, 0), center_offset_x=end_column_compound_width / 2, center_offset_y=-compound_key_height_small / 2 - pinky_offset / 4),
                                    Key(steno="&S", grid_location=(0, 1), center_offset_y=compound_key_height_small / 2),
                                    Key(steno="&@S", grid_location=(1, 1)),
                                    Key(steno="@S", grid_location=(2, 1), center_offset_y=-compound_key_height_small / 2 - pinky_offset / 4),
                                    Key(steno="S", label="S", grid_location=(0, 2, 3, 1), center_offset_x=-pinky_stretch / 2 - end_column_compound_width / 2, center_offset_y=-pinky_offset / 4),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_RIGHT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=-settings.key_width_ref,
                                y=-ring_offset / 2,
    
                                elements=(
                                    Key(steno="T", label="T", height=reduced_key_height, center_offset_y=compound_key_size / 2),
                                    Key(steno="TK", height=compound_key_size),
                                    Key(steno="K", label="K", height=reduced_key_height + ring_offset / 2, center_offset_y=-compound_key_size / 2 - ring_offset / 4),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_RIGHT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=Ref(0),
                                y=-middle_offset / 2,
    
                                elements=(
                                    Key(steno="P", label="P", height=reduced_key_height, center_offset_y=compound_key_size / 2),
                                    Key(steno="PW", height=compound_key_size),
                                    Key(steno="W", label="W", height=reduced_key_height + middle_offset / 2, center_offset_y=-compound_key_size / 2 - middle_offset / 4),
                                ),
                            ),
                    
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_LEFT,
                                organization=GroupOrganization.grid(
                                    row_heights=(
                                        reduced_key_height_small,
                                        compound_key_height_small,
                                        reduced_key_height_small + index_offset / 2,
                                    ),
                                    col_widths=(reduced_index_width, index_compound_width, middle_key_width),
                                ),

                                x=Ref(0),
                                y=-index_offset / 2,

                                elements=(
                                    Key(steno="^", label="^", grid_location=(0, 2, 3, 1), center_offset_x=-key_width / 4 - index_compound_width / 2, center_offset_y=-index_offset / 4),
                                    Key(steno="H", label="H", grid_location=(0, 0), center_offset_x=index_compound_width / 2 + index_stretch / 2, center_offset_y=compound_key_height_small / 2),
                                    Key(steno="HR", grid_location=(1, 0), center_offset_x=index_compound_width / 2 + index_stretch / 2),
                                    Key(steno="R", label="R", grid_location=(2, 0)),
                                    Key(steno="^H", grid_location=(0, 1), center_offset_y=compound_key_height_small / 2),
                                    Key(steno="^HR", grid_location=(1, 1), center_offset_x=index_compound_width / 2 + index_stretch / 2, center_offset_y=-compound_key_height_small / 2 - index_offset / 4),
                                    Key(steno="^R", grid_location=(2, 1), center_offset_y=-compound_key_height_small / 2 - index_offset / 4),
                                ),
                            ),
                        ),
                    ),
                    KeyGroup(
                        alignment=GroupAlignment.TOP_LEFT,
                        organization=GroupOrganization.grid(
                            row_heights=vowel_set_heights,
                            col_widths=(
                                reduced_key_width + VOWEL_KEY_WIDTH_BOOST,
                                compound_key_size,
                                reduced_key_width + VOWEL_KEY_WIDTH_BOOST,
                            ),
                        ),

                        x=-(settings.vowel_set_offset_fac_ref * settings.key_width_ref),
                        y=settings.row_spacing_ref,

                        angle=settings.vowel_rows_angle_ref,

                        elements=(
                            Key(steno="#", label="#", grid_location=(2, 0, 1, 3), center_offset_y=-vowel_compound_height / 2),
                            Key(steno="A", label="A", grid_location=(0, 0), center_offset_x=VOWEL_KEY_WIDTH_BOOST / 2 + compound_key_size / 2, center_offset_y=vowel_compound_height / 2),
                            Key(steno="AO", grid_location=(0, 1), center_offset_y=vowel_compound_height / 2),
                            Key(steno="O", label="O", grid_location=(0, 2), center_offset_x=-VOWEL_KEY_WIDTH_BOOST / 2 - compound_key_size / 2, center_offset_y=vowel_compound_height / 2),
                            Key(steno="#A", grid_location=(1, 0), center_offset_x=VOWEL_KEY_WIDTH_BOOST / 2 + compound_key_size / 2),
                            Key(steno="#AO", grid_location=(1, 1)),
                            Key(steno="#O", grid_location=(1, 2), center_offset_x=-VOWEL_KEY_WIDTH_BOOST / 2 - compound_key_size / 2),
                        ),
                    ),
                ),
            ),

            Group(
                alignment=GroupAlignment.TOP_LEFT,

                x=index_group_width + settings.bank_spacing_ref / 2,
                y=Ref(0),
                angle=-settings.main_rows_angle_ref,

                adaptive_transform=True,

                elements=(
                    KeyGroup(
                        alignment=GroupAlignment.TOP_RIGHT,
                        organization=GroupOrganization.grid(
                            row_heights=vowel_set_heights,
                            col_widths=(
                                reduced_key_width + VOWEL_KEY_WIDTH_BOOST,
                                compound_key_size,
                                reduced_key_width + VOWEL_KEY_WIDTH_BOOST,
                            ),
                        ),

                        x=settings.vowel_set_offset_fac_ref * settings.key_width_ref,
                        y=settings.row_spacing_ref,

                        angle=-settings.vowel_rows_angle_ref,

                        elements=(
                            Key(steno="_", label="_", grid_location=(2, 0, 1, 3), center_offset_y=-vowel_compound_height / 2),
                            Key(steno="E", label="E", grid_location=(0, 0), center_offset_x=VOWEL_KEY_WIDTH_BOOST / 2 + compound_key_size / 2, center_offset_y=vowel_compound_height / 2),
                            Key(steno="EU", grid_location=(0, 1), center_offset_y=vowel_compound_height / 2),
                            Key(steno="U", label="U", grid_location=(0, 2), center_offset_x=-VOWEL_KEY_WIDTH_BOOST / 2 - compound_key_size / 2, center_offset_y=vowel_compound_height / 2),
                            Key(steno="_E", grid_location=(1, 0), center_offset_x=VOWEL_KEY_WIDTH_BOOST / 2 + compound_key_size / 2),
                            Key(steno="_EU", grid_location=(1, 1)),
                            Key(steno="_U", grid_location=(1, 2), center_offset_x=-VOWEL_KEY_WIDTH_BOOST / 2 - compound_key_size / 2),
                        ),
                    ),
                    Group(
                        alignment=GroupAlignment.TOP_LEFT,
    
                        x=Ref(0),
                        y=Ref(0),
    
                        elements=(
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_RIGHT,
                                organization=GroupOrganization.grid(
                                    row_heights=(reduced_key_height_small, compound_key_height_small, reduced_key_height_small + index_offset / 2),
                                    col_widths=(middle_key_width, index_compound_width, reduced_index_width),
                                ),

                                x=Ref(0),
                                y=-index_offset / 2,

                                elements=(
                                    Key(steno="*", label="🞱", grid_location=(0, 0, 3, 1), center_offset_x=key_width / 4 + index_compound_width / 2, center_offset_y=-index_offset / 4),
                                    Key(steno="*F", grid_location=(0, 1), center_offset_y=compound_key_height_small / 2),
                                    Key(steno="*FR", grid_location=(1, 1)),
                                    Key(steno="*R", grid_location=(2, 1), center_offset_y=-compound_key_height_small / 2 - index_offset / 4),
                                    Key(steno="-F", label="F", grid_location=(0, 2), center_offset_x=-index_compound_width / 2 - index_stretch / 2, center_offset_y=compound_key_height_small / 2),
                                    Key(steno="-FR", grid_location=(1, 2), center_offset_x=-index_compound_width / 2 - index_stretch / 2),
                                    Key(steno="-R", label="R", grid_location=(2, 2), center_offset_x=-index_compound_width / 2 - index_stretch / 2, center_offset_y=-compound_key_height_small / 2 - index_offset / 4),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_LEFT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=Ref(0),
                                y=-middle_offset / 2,
    
                                elements=(
                                    Key(steno="-P", label="P", height=reduced_key_height, center_offset_y=compound_key_size / 2),
                                    Key(steno="-PB", height=compound_key_size),
                                    Key(steno="-B", label="B", height=reduced_key_height + middle_offset / 2, center_offset_y=-compound_key_size / 2 - middle_offset / 4),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_LEFT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=settings.key_width_ref,
                                y=-ring_offset / 2,
    
                                elements=(
                                    Key(steno="-L", label="L", height=reduced_key_height, center_offset_y=compound_key_size / 2),
                                    Key(steno="-LG", height=compound_key_size),
                                    Key(steno="-G", label="G", height=reduced_key_height + ring_offset / 2, center_offset_y=-compound_key_size / 2 - ring_offset / 4),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_LEFT,
                                organization=GroupOrganization.grid(
                                    row_heights=(
                                        reduced_key_height_small,
                                        compound_key_height_small,
                                        reduced_key_height_small + pinky_offset / 2,
                                    ),
                                    col_widths=(
                                        reduced_key_width + pinky_stretch,
                                        end_column_compound_width,
                                        end_column_width,
                                    ),
                                ),
    
                                x=2 * settings.key_width_ref,
                                y=-pinky_offset / 2,
    
                                elements=(
                                    Key(steno="-T", label="T", grid_location=(0, 0), center_offset_x=pinky_stretch / 2 + end_column_compound_width / 2, center_offset_y=compound_key_height_small / 2),
                                    Key(steno="-TS", grid_location=(1, 0), center_offset_x=pinky_stretch / 2 + end_column_compound_width / 2),
                                    Key(steno="-S", label="S", grid_location=(2, 0), center_offset_x=pinky_stretch / 2 + end_column_compound_width / 2, center_offset_y=-compound_key_height_small / 2 - pinky_offset / 4),
                                    Key(steno="-TD", grid_location=(0, 1), center_offset_y=compound_key_height_small / 2),
                                    Key(steno="-TSDZ", grid_location=(1, 1)),
                                    Key(steno="-SZ", grid_location=(2, 1), center_offset_y=-compound_key_height_small / 2 - pinky_offset / 4),
                                    Key(steno="-D", label="D", grid_location=(0, 2), center_offset_x=-end_column_compound_width / 2, center_offset_y=compound_key_height_small / 2),
                                    Key(steno="-DZ", grid_location=(1, 2), center_offset_x=-end_column_compound_width / 2),
                                    Key(steno="-Z", label="Z", grid_location=(2, 2), center_offset_x=-end_column_compound_width / 2, center_offset_y=-compound_key_height_small / 2 - pinky_offset / 4),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )