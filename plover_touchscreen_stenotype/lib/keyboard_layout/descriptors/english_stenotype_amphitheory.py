from typing import Callable, TYPE_CHECKING

from .common import build_common_params
from ...reactivity import Ref, computed
from ..LayoutDescriptor import LayoutDescriptor, Key, KeyGroup, Group, GroupAlignment, GroupOrganization
if TYPE_CHECKING:
    from ....settings import Settings
    from ....widgets.keyboard.KeyboardWidget import KeyboardWidget
else:
    Settings = object
    KeyboardWidget = object

def build_layout_descriptor(settings: Settings, keyboard_widget: KeyboardWidget) -> LayoutDescriptor:
    common_params = build_common_params(settings, keyboard_widget)
    
    key_width = common_params.key_width
    key_height = common_params.key_height
    compound_key_size = common_params.compound_key_size
    reduced_size = common_params.reduced_size

    reduced_key_width = common_params.reduced_key_width
    reduced_key_height = common_params.reduced_key_height

    index_stretch = common_params.index_stretch
    pinky_stretch = common_params.pinky_stretch

    compound_key_height_small = common_params.compound_key_height_small
    reduced_key_height_small = common_params.reduced_key_height_small

        
    index_compound_width = common_params.index_compound_width
    reduced_index_width = common_params.reduced_index_width
    middle_key_width = common_params.middle_key_width


    end_column_compound_width = common_params.end_column_compound_width
        
    end_column_width = common_params.end_column_width

    index_offset = common_params.index_offset
    middle_offset = common_params.middle_offset
    ring_offset = common_params.ring_offset
    pinky_offset = common_params.pinky_offset


    vowel_key_width_boost = common_params.vowel_key_width_boost

    bank_offset = common_params.bank_offset
    vowel_set_offset = common_params.vowel_set_offset

    vowel_compound_height = index_compound_width
    vowel_set_heights = (
        reduced_size(key_height, vowel_compound_height),
        vowel_compound_height,
        reduced_size(key_height * 0.75, vowel_compound_height),
    )

    asterisk_row_heights = (
        reduced_key_height_small,
        compound_key_height_small,
        reduced_key_height_small + index_offset / 2,
    )

    #endregion


    return LayoutDescriptor(
        elements=(
            Group(
                alignment=GroupAlignment.TOP_LEFT,

                x=-bank_offset,
                y=Ref(0),
                angle=settings.bank_angle_ref,

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
                                    row_heights=asterisk_row_heights,
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
                                reduced_key_width + vowel_key_width_boost,
                                compound_key_size,
                                reduced_key_width + vowel_key_width_boost,
                            ),
                        ),

                        x=-vowel_set_offset,
                        y=settings.row_spacing_ref,

                        angle=settings.vowel_angle_ref,

                        elements=(
                            Key(steno="#", label="#", grid_location=(2, 0, 1, 3), center_offset_y=-vowel_compound_height / 2),
                            Key(steno="A", label="A", grid_location=(0, 0), center_offset_x=vowel_key_width_boost / 2 + compound_key_size / 2, center_offset_y=vowel_compound_height / 2),
                            Key(steno="AO", grid_location=(0, 1), center_offset_y=vowel_compound_height / 2),
                            Key(steno="O", label="O", grid_location=(0, 2), center_offset_x=-vowel_key_width_boost / 2 - compound_key_size / 2, center_offset_y=vowel_compound_height / 2),
                            Key(steno="#A", grid_location=(1, 0), center_offset_x=vowel_key_width_boost / 2 + compound_key_size / 2),
                            Key(steno="#AO", grid_location=(1, 1)),
                            Key(steno="#O", grid_location=(1, 2), center_offset_x=-vowel_key_width_boost / 2 - compound_key_size / 2),
                        ),
                    ),
                ),
            ),

            Group(
                alignment=GroupAlignment.TOP_LEFT,

                x=bank_offset,
                y=Ref(0),
                angle=-settings.bank_angle_ref,

                adaptive_transform=True,

                elements=(
                    KeyGroup(
                        alignment=GroupAlignment.TOP_RIGHT,
                        organization=GroupOrganization.grid(
                            row_heights=vowel_set_heights,
                            col_widths=(
                                reduced_key_width + vowel_key_width_boost,
                                compound_key_size,
                                reduced_key_width + vowel_key_width_boost,
                            ),
                        ),

                        x=vowel_set_offset,
                        y=settings.row_spacing_ref,

                        angle=-settings.vowel_angle_ref,

                        elements=(
                            Key(steno="_", label="_", grid_location=(2, 0, 1, 3), center_offset_y=-vowel_compound_height / 2),
                            Key(steno="E", label="E", grid_location=(0, 0), center_offset_x=vowel_key_width_boost / 2 + compound_key_size / 2, center_offset_y=vowel_compound_height / 2),
                            Key(steno="EU", grid_location=(0, 1), center_offset_y=vowel_compound_height / 2),
                            Key(steno="U", label="U", grid_location=(0, 2), center_offset_x=-vowel_key_width_boost / 2 - compound_key_size / 2, center_offset_y=vowel_compound_height / 2),
                            Key(steno="_E", grid_location=(1, 0), center_offset_x=vowel_key_width_boost / 2 + compound_key_size / 2),
                            Key(steno="_EU", grid_location=(1, 1)),
                            Key(steno="_U", grid_location=(1, 2), center_offset_x=-vowel_key_width_boost / 2 - compound_key_size / 2),
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
                                    row_heights=asterisk_row_heights,
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