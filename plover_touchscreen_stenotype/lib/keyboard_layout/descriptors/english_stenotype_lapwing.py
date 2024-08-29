from typing import TYPE_CHECKING

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

    reduced_key_width = common_params.reduced_key_width
    reduced_key_height = common_params.reduced_key_height


    pinky_stretch = common_params.pinky_stretch

    compound_key_height_small = common_params.compound_key_height_small
    reduced_key_height_small = common_params.reduced_key_height_small

        
    index_compound_width = common_params.index_compound_width
    reduced_index_width = common_params.reduced_index_width
    middle_key_width = common_params.middle_key_width


    end_column_compound_width = common_params.end_column_compound_width
        
    end_column_width = common_params.end_column_width
    inner_end_column_width = common_params.inner_end_column_width

    index_offset = common_params.index_offset
    middle_offset = common_params.middle_offset
    ring_offset = common_params.ring_offset
    pinky_offset = common_params.pinky_offset


    num_bar_affected_label = common_params.num_bar_affected_label

    vowel_key_width_boost = common_params.vowel_key_width_boost
    end_column_width_boost = common_params.end_column_width_boost

    bank_offset = common_params.bank_offset
    vowel_set_offset = common_params.vowel_set_offset


    asterisk_row_heights = (
        reduced_key_height_small,
        compound_key_height_small,
        reduced_key_height_small + index_offset / 2,
    )


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
                                organization=GroupOrganization.vertical(key_width + pinky_stretch + end_column_width_boost),
    
                                x=-2 * settings.key_width_ref,
                                y=-pinky_offset / 2,
    
                                elements=(
                                    Key(steno="#", label="#", height=reduced_key_height_small),
                                    Key(steno="#S", height=compound_key_height_small),
                                    Key(steno="S", label=num_bar_affected_label("S", "1"), height=reduced_key_height_small + pinky_offset / 2),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_RIGHT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=-settings.key_width_ref,
                                y=-ring_offset / 2,
    
                                elements=(
                                    Key(steno="T", label=num_bar_affected_label("T", "2"), height=reduced_key_height),
                                    Key(steno="TK", height=compound_key_size),
                                    Key(steno="K", label="K", height=reduced_key_height + ring_offset / 2),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_RIGHT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=Ref(0),
                                y=-middle_offset / 2,
    
                                elements=(
                                    Key(steno="P", label=num_bar_affected_label("P", "3"), height=reduced_key_height),
                                    Key(steno="PW", height=compound_key_size),
                                    Key(steno="W", label="W", height=reduced_key_height + middle_offset / 2),
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
                                    Key(steno="*", label="🞱", grid_location=(0, 2, 3, 1)),
                                    Key(steno="H", label=num_bar_affected_label("H", "4"), grid_location=(0, 0)),
                                    Key(steno="HR", grid_location=(1, 0)),
                                    Key(steno="R", label="R", grid_location=(2, 0)),
                                    Key(steno="H*", grid_location=(0, 1)),
                                    Key(steno="HR*", grid_location=(1, 1)),
                                    Key(steno="R*", grid_location=(2, 1)),
                                ),
                            ),
                        ),
                    ),
                    KeyGroup(
                        alignment=GroupAlignment.TOP_LEFT,
                        organization=GroupOrganization.horizontal(key_height),

                        x=-vowel_set_offset,
                        y=settings.row_spacing_ref,

                        angle=settings.vowel_angle_ref,

                        elements=(
                            Key(steno="A", label=num_bar_affected_label("A", "5"), width=reduced_key_width + vowel_key_width_boost),
                            Key(steno="AO", width=compound_key_size),
                            Key(steno="O", label=num_bar_affected_label("O", "0"), width=reduced_key_width + vowel_key_width_boost),
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
                        organization=GroupOrganization.horizontal(key_height),

                        x=vowel_set_offset,
                        y=settings.row_spacing_ref,

                        angle=-settings.vowel_angle_ref,

                        elements=(
                            Key(steno="E", label="E", width=reduced_key_width + vowel_key_width_boost),
                            Key(steno="EU", width=compound_key_size),
                            Key(steno="U", label="U", width=reduced_key_width + vowel_key_width_boost),
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
                                    Key(steno="*", label="🞱", grid_location=(0, 0, 3, 1)),
                                    Key(steno="*F", grid_location=(0, 1)),
                                    Key(steno="*FR", grid_location=(1, 1)),
                                    Key(steno="*R", grid_location=(2, 1)),
                                    Key(steno="-F", label=num_bar_affected_label("F", "6"), grid_location=(0, 2)),
                                    Key(steno="-FR", grid_location=(1, 2)),
                                    Key(steno="-R", label="R", grid_location=(2, 2)),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_LEFT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=Ref(0),
                                y=-middle_offset / 2,
    
                                elements=(
                                    Key(steno="-P", label=num_bar_affected_label("P", "7"), height=reduced_key_height),
                                    Key(steno="-PB", height=compound_key_size),
                                    Key(steno="-B", label="B", height=reduced_key_height + middle_offset / 2),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_LEFT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=settings.key_width_ref,
                                y=-ring_offset / 2,
    
                                elements=(
                                    Key(steno="-L", label=num_bar_affected_label("L", "8"), height=reduced_key_height),
                                    Key(steno="-LG", height=compound_key_size),
                                    Key(steno="-G", label="G", height=reduced_key_height + ring_offset / 2),
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
                                        inner_end_column_width,
                                        end_column_compound_width,
                                        end_column_width,
                                    ),
                                ),
    
                                x=2 * settings.key_width_ref,
                                y=-pinky_offset / 2,
    
                                elements=(
                                    Key(steno="-T", label=num_bar_affected_label("T", "9"), grid_location=(0, 0)),
                                    Key(steno="-TS", grid_location=(1, 0)),
                                    Key(steno="-S", label="S", grid_location=(2, 0)),
                                    Key(steno="-TD", grid_location=(0, 1)),
                                    Key(steno="-TSDZ", grid_location=(1, 1)),
                                    Key(steno="-SZ", grid_location=(2, 1)),
                                    Key(steno="-D", label="D", grid_location=(0, 2)),
                                    Key(steno="-DZ", grid_location=(1, 2)),
                                    Key(steno="-Z", label="Z", grid_location=(2, 2)),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),

        out_center_diff=-key_width,
    )