from math import sin, cos, radians
from typing import Callable, TYPE_CHECKING
from dataclasses import dataclass

from ...reactivity import Ref, computed
if TYPE_CHECKING:
    from ....settings import Settings
    from ....widgets.keyboard.KeyboardWidget import KeyboardWidget
else:
    Settings = object
    KeyboardWidget = object


@dataclass
class CommonParams:
    key_width: Ref[float]
    key_height: Ref[float]

    compound_key_size: Ref[float]

    reduced_size: Callable[[Ref[float], Ref[float]], Ref[float]]
    """Computes the size of a key that has half of a compound key cutting into it"""

    reduced_key_width: Ref[float]
    reduced_key_height: Ref[float]

    num_bar_key_height: Ref[float]

    compound_key_height_small: Ref[float]
    reduced_key_height_small: Ref[float]

    index_stretch: Ref[float]
    pinky_stretch: Ref[float]
    
    index_compound_width: Ref[float]
    base_index_width: Ref[float]
    reduced_index_width: Ref[float]
    middle_key_width: Ref[float]


    end_column_compound_width: Ref[float]
    
    end_column_width: Ref[float]
    inner_end_column_width: Ref[float]

    index_offset: Ref[float]
    middle_offset: Ref[float]
    ring_offset: Ref[float]
    pinky_offset: Ref[float]


    index_group_width: Ref[float]

    num_bar_affected_label: Callable[[str, str], Ref[str]]

    vowel_key_width_boost: float
    end_column_width_boost: float

    bank_offset: Ref[float]
    vowel_set_offset: Ref[float]



def build_common_params(settings: Settings, keyboard_widget: KeyboardWidget):
    #region Size values

    key_width = settings.key_width_ref
    key_height = settings.key_height_ref
    compound_key_size = settings.compound_key_size_ref

    reduced_size: Callable[[Ref[float], Ref[float]], Ref[float]] = lambda key_size_ref, compound_size_ref: key_size_ref - compound_size_ref / 2

    reduced_key_width = reduced_size(key_width, compound_key_size)
    reduced_key_height = reduced_size(key_height, compound_key_size)

    num_bar_key_height = key_height / 2

    index_stretch = settings.index_stretch_ref
    pinky_stretch = settings.pinky_stretch_ref

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


    def num_bar_affected_label(default_label: str, number_label: str):
        return computed(lambda: number_label if keyboard_widget.num_bar_pressed else default_label,
                keyboard_widget.num_bar_pressed_ref)
    

    return CommonParams(
        key_width=key_width,
        key_height=key_height,
        compound_key_size=compound_key_size,
        reduced_size=reduced_size,

        reduced_key_width=reduced_key_width,
        reduced_key_height=reduced_key_height,

        num_bar_key_height=num_bar_key_height,

        index_stretch=index_stretch,
        pinky_stretch=pinky_stretch,

        compound_key_height_small=compound_key_height_small,
        reduced_key_height_small=reduced_key_height_small,

        
        index_compound_width=index_compound_width,
        base_index_width=base_index_width,
        reduced_index_width=reduced_index_width,
        middle_key_width=middle_key_width,


        end_column_compound_width=end_column_compound_width,
        
        end_column_width=end_column_width,
        inner_end_column_width=inner_end_column_width,

        index_offset=index_offset,
        middle_offset=middle_offset,
        ring_offset=ring_offset,
        pinky_offset=pinky_offset,


        index_group_width=index_group_width,

        num_bar_affected_label=num_bar_affected_label,

        vowel_key_width_boost=VOWEL_KEY_WIDTH_BOOST,
        end_column_width_boost=END_COLUMN_WIDTH_BOOST,

        bank_offset=index_group_width + settings.bank_spacing_ref / 2,
        vowel_set_offset=settings.vowel_set_offset_fac_ref * settings.key_width_ref,
    )

