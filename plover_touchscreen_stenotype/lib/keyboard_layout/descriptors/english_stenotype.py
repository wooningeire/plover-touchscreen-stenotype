from math import sin, cos, radians
from typing import Callable, TYPE_CHECKING

from ...reactivity import Ref, computed
from ..LayoutDescriptor import LayoutDescriptor, Key, KeyGroup, Group, GroupAlignment, GroupOrganization
if TYPE_CHECKING:
    from ....settings import Settings
    from ....widgets.keyboard.KeyboardWidget import KeyboardWidget
else:
    Settings = object
    KeyboardWidget = object


def build_layout_descriptor(settings: Settings, keyboard_widget: KeyboardWidget) -> LayoutDescriptor:
    def _num_bar_affected_label(default_label: str, number_label: str):
        return computed(lambda: number_label if keyboard_widget.num_bar_pressed else default_label,
                keyboard_widget.num_bar_pressed_ref)

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
                                organization=GroupOrganization.vertical(key_width + pinky_stretch + END_COLUMN_WIDTH_BOOST),
    
                                x=-2 * settings.key_width_ref,
                                y=-pinky_offset / 2,
    
                                elements=(
                                    Key(steno="#", label="#", height=reduced_key_height_small),
                                    Key(steno="#S", height=compound_key_height_small),
                                    Key(steno="S", label=_num_bar_affected_label("S", "1"), height=reduced_key_height_small + pinky_offset / 2),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_RIGHT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=-settings.key_width_ref,
                                y=-ring_offset / 2,
    
                                elements=(
                                    Key(steno="T", label=_num_bar_affected_label("T", "2"), height=reduced_key_height),
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
                                    Key(steno="P", label=_num_bar_affected_label("P", "3"), height=reduced_key_height),
                                    Key(steno="PW", height=compound_key_size),
                                    Key(steno="W", label="W", height=reduced_key_height + middle_offset / 2),
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
                                    Key(steno="*", label="🞱", grid_location=(0, 2, 3, 1)),
                                    Key(steno="H", label=_num_bar_affected_label("H", "4"), grid_location=(0, 0)),
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

                        x=-(settings.vowel_set_offset_fac_ref * settings.key_width_ref),
                        y=settings.row_spacing_ref,

                        angle=settings.vowel_angle_ref,

                        elements=(
                            Key(steno="A", label=_num_bar_affected_label("A", "5"), width=reduced_key_width + VOWEL_KEY_WIDTH_BOOST),
                            Key(steno="AO", width=compound_key_size),
                            Key(steno="O", label=_num_bar_affected_label("O", "0"), width=reduced_key_width + VOWEL_KEY_WIDTH_BOOST),
                        ),
                    ),
                ),
            ),

            Group(
                alignment=GroupAlignment.TOP_LEFT,

                x=index_group_width + settings.bank_spacing_ref / 2,
                y=Ref(0),
                angle=-settings.bank_angle_ref,

                adaptive_transform=True,

                elements=(
                    KeyGroup(
                        alignment=GroupAlignment.TOP_RIGHT,
                        organization=GroupOrganization.horizontal(key_height),

                        x=settings.vowel_set_offset_fac_ref * settings.key_width_ref,
                        y=settings.row_spacing_ref,

                        angle=-settings.vowel_angle_ref,

                        elements=(
                            Key(steno="E", label="E", width=reduced_key_width + VOWEL_KEY_WIDTH_BOOST),
                            Key(steno="EU", width=compound_key_size),
                            Key(steno="U", label="U", width=reduced_key_width + VOWEL_KEY_WIDTH_BOOST),
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
                                    Key(steno="*", label="🞱", grid_location=(0, 0, 3, 1)),
                                    Key(steno="*F", grid_location=(0, 1)),
                                    Key(steno="*FR", grid_location=(1, 1)),
                                    Key(steno="*R", grid_location=(2, 1)),
                                    Key(steno="-F", label=_num_bar_affected_label("F", "6"), grid_location=(0, 2)),
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
                                    Key(steno="-P", label=_num_bar_affected_label("P", "7"), height=reduced_key_height),
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
                                    Key(steno="-L", label=_num_bar_affected_label("L", "8"), height=reduced_key_height),
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
                                    Key(steno="-T", label=_num_bar_affected_label("T", "9"), grid_location=(0, 0)),
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