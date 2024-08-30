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

    num_bar_affected_label = common_params.num_bar_affected_label
    
    key_width = common_params.key_width
    key_height = common_params.key_height
    compound_key_size = common_params.compound_key_size

    reduced_size = common_params.reduced_size

    reduced_key_height = common_params.reduced_key_height



    compound_key_size_small = common_params.compound_key_height_small
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


    vowel_key_width_boost = common_params.vowel_key_width_boost

    bank_offset = common_params.bank_offset
    vowel_set_offset = common_params.vowel_set_offset


    reduced_key_width_small = reduced_size(key_width, compound_key_size_small)
    double_reduced_key_width_small = reduced_size(reduced_key_width_small, compound_key_size_small)
    double_reduced_key_height_small = reduced_size(reduced_key_height_small, compound_key_size_small)


    index_row_heights = (
        reduced_key_height_small,
        compound_key_size_small,
        double_reduced_key_height_small,
        compound_key_size_small,
        reduced_key_height_small + index_offset / 2,
    )

    pinky_row_heights = (
        reduced_key_height_small,
        compound_key_size_small,
        reduced_key_height_small + pinky_offset / 2,
    )

    palm_key_width = key_width * 2
    palm_key_height = key_height * 1.5


    return LayoutDescriptor(
        elements=(
            Group(
                alignment=GroupAlignment.TOP_LEFT,

                x=-bank_offset,
                y=Ref(0),
                angle=settings.bank_angle_ref,

                adaptive_transform=True,

                elements=(
                    KeyGroup(
                        alignment=GroupAlignment.TOP_RIGHT,
                        organization=GroupOrganization.grid(
                            row_heights=(palm_key_height,),
                            col_widths=(palm_key_width,),
                        ),

                        x=-1.5 * key_width,
                        y=2 * key_height,

                        elements=(
                            Key(steno="H", label=num_bar_affected_label("CAPITAL", "CAPITAL<br /><small>H</small>"), grid_location=(0, 0)),
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
                                    row_heights=pinky_row_heights,
                                    col_widths=(
                                        end_column_width,
                                        end_column_compound_width,
                                        inner_end_column_width,
                                    ),
                                ),
    
                                x=-2 * key_width,
                                y=-pinky_offset / 2,
    
                                elements=(
                                    Key(steno="Z", label=num_bar_affected_label("Z", "Z<br /><small>@</small>"), grid_location=(0, 0, 3, 1)),
                                    Key(steno="ZF", grid_location=(0, 1)),
                                    Key(steno="ZFS", grid_location=(1, 1)),
                                    Key(steno="ZS", grid_location=(2, 1)),
                                    Key(steno="F", label=num_bar_affected_label("F<br /><small>+ C → Q</small>", "F<br /><small>£</small>"), grid_location=(0, 2)),
                                    Key(steno="FS", grid_location=(1, 2)),
                                    Key(steno="S", label=num_bar_affected_label("S", "S<br /><small>$</small>"), grid_location=(2, 2)),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_RIGHT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=-key_width,
                                y=-ring_offset / 2,
    
                                elements=(
                                    Key(steno="P", label=num_bar_affected_label("P<br /><small>+ J → B</small>", "P<br /><small>%</small>"), height=reduced_key_height_small),
                                    Key(steno="PT", height=compound_key_size_small),
                                    Key(steno="T", label=num_bar_affected_label("T<br /><small>+ J → D</small>", "T<br /><small>/</small>"), height=double_reduced_key_height_small),
                                    Key(steno="TC", height=compound_key_size_small),
                                    Key(steno="C", label=num_bar_affected_label("C<br /><small>+ J → G</small>", "C<br /><small>(</small>"), height=reduced_key_height_small + ring_offset / 2),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_RIGHT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=Ref(0),
                                y=-middle_offset / 2,
    
                                elements=(
                                    Key(steno="K", label=num_bar_affected_label("K<br /><small>+ Z → X</small>", "K<br /><small>&</small>"), height=reduced_key_height_small),
                                    Key(steno="KJ", height=compound_key_size_small),
                                    Key(steno="J", label=num_bar_affected_label("J<br /><small>+ L → H</small>", "J<br /><small>*</small>"), height=double_reduced_key_height_small),
                                    Key(steno="JR", height=compound_key_size_small),
                                    Key(steno="R", label=num_bar_affected_label("R<br /><small>+ N → M</small>", "R<br /><small>+</small>"), height=reduced_key_height_small + middle_offset / 2),
                                ),
                            ),
                    
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_LEFT,
                                organization=GroupOrganization.grid(
                                    row_heights=index_row_heights,
                                    col_widths=(reduced_index_width, index_compound_width, middle_key_width),
                                ),

                                x=Ref(0),
                                y=-index_offset / 2,

                                elements=(
                                    Key(steno="I", label=num_bar_affected_label("I", "I<br /><small>7</small>"), grid_location=(0, 0)),
                                    Key(steno="IO", grid_location=(1, 0)),
                                    Key(steno="O", label=num_bar_affected_label("O<br /><small>+ I → A</small>", "O<br /><small>4</small>"), grid_location=(2, 0)),
                                    Key(steno="OE", grid_location=(3, 0)),
                                    Key(steno="E", label=num_bar_affected_label("E", "E<br /><small>1</small>"), grid_location=(4, 0)),
                                    Key(steno="I'", grid_location=(0, 1)),
                                    Key(steno="IO'U", grid_location=(1, 1)),
                                    Key(steno="OU", grid_location=(2, 1)),
                                    Key(steno="OEUA", grid_location=(3, 1)),
                                    Key(steno="EA", grid_location=(4, 1)),
                                    Key(steno="'", label=num_bar_affected_label("'", "'<br /><small>8</small>"), grid_location=(0, 2)),
                                    Key(steno="'U", grid_location=(1, 2)),
                                    Key(steno="U", label=num_bar_affected_label("U", "U<br /><small>5</small>"), grid_location=(2, 2)),
                                    Key(steno="UA", grid_location=(3, 2)),
                                    Key(steno="A", label=num_bar_affected_label("A", "A<br /><small>2</small>"), grid_location=(4, 2)),
                                ),
                            ),
                        ),
                    ),
                    KeyGroup(
                        alignment=GroupAlignment.TOP_LEFT,
                        organization=GroupOrganization.grid(
                            row_heights=(reduced_key_height_small, compound_key_size_small, reduced_key_height_small),
                            col_widths=(reduced_key_width_small + vowel_key_width_boost, compound_key_size_small, double_reduced_key_width_small, compound_key_size_small, reduced_key_width_small + vowel_key_width_boost),
                        ),

                        x=-vowel_set_offset,
                        y=settings.row_spacing_ref,

                        angle=settings.vowel_angle_ref,

                        elements=(
                            Key(steno="L", label=num_bar_affected_label("L<br /><small>+ R → V</small>", "L<br /><small>€</small>"), grid_location=(0, 0, 2, 1)),
                            Key(steno="LN", grid_location=(0, 1)),
                            Key(steno="N", label=num_bar_affected_label("N<br /><small>+ J → W</small>", "N<br /><small>.</small>"), grid_location=(0, 2)),
                            Key(steno="NY", grid_location=(0, 3)),
                            Key(steno="Y", label=num_bar_affected_label("Y", "Y<br /><small>0</small>"), grid_location=(0, 4)),
                            Key(steno="LN´", grid_location=(1, 1)),
                            Key(steno="N´", grid_location=(1, 2)),
                            Key(steno="#N´Y", grid_location=(1, 3)),
                            Key(steno="#Y", grid_location=(1, 4)),
                            Key(steno="´", label=num_bar_affected_label("´", "´<br /><small>~</small>"), grid_location=(2, 1, 1, 2)),
                            Key(steno="#´", grid_location=(2, 3)),
                            Key(steno="#", label="SHIFT", grid_location=(2, 4)),
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
                            row_heights=(reduced_key_height_small, compound_key_size_small, reduced_key_height_small),
                            col_widths=(reduced_key_width_small + vowel_key_width_boost, compound_key_size_small, double_reduced_key_width_small, compound_key_size_small, reduced_key_width_small + vowel_key_width_boost),
                        ),

                        x=vowel_set_offset,
                        y=settings.row_spacing_ref,

                        angle=-settings.vowel_angle_ref,

                        elements=(
                            Key(steno="-Y", label=num_bar_affected_label("Y", "Y<br /><small>0</small>"), grid_location=(0, 0)),
                            Key(steno="-YN", grid_location=(0, 1)),
                            Key(steno="-N", label=num_bar_affected_label("N<br /><small>+ J → W</small>", "N<br /><small>,</small>"), grid_location=(0, 2)),
                            Key(steno="-NL", grid_location=(0, 3)),
                            Key(steno="-L", label=num_bar_affected_label("L<br /><small>+ R → V</small>", "L<br /><small>_</small>"), grid_location=(0, 4, 2, 1)),
                            Key(steno="#-Y", grid_location=(1, 0)),
                            Key(steno="#-Y`N", grid_location=(1, 1)),
                            Key(steno="-`N", grid_location=(1, 2)),
                            Key(steno="-`NL", grid_location=(1, 3)),
                            Key(steno="#", label="SHIFT", grid_location=(2, 0)),
                            Key(steno="#-`", grid_location=(2, 1)),
                            Key(steno="-`", label=num_bar_affected_label("`", "`<br /><small>¨</small>"), grid_location=(2, 2, 1, 2)),
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
                                    row_heights=index_row_heights,
                                    col_widths=(middle_key_width, index_compound_width, reduced_index_width),
                                ),

                                x=Ref(0),
                                y=-index_offset / 2,

                                elements=(
                                    Key(steno="-'", label=num_bar_affected_label("'", "'<br /><small>8</small>"), grid_location=(0, 0)),
                                    Key(steno="-U'", grid_location=(1, 0)),
                                    Key(steno="-U", label=num_bar_affected_label("U", "U<br /><small>5</small>"), grid_location=(2, 0)),
                                    Key(steno="-AU", grid_location=(3, 0)),
                                    Key(steno="-A", label=num_bar_affected_label("A", "A<br /><small>2</small>"), grid_location=(4, 0)),
                                    Key(steno="-'O", grid_location=(0, 1)),
                                    Key(steno="-U'OI", grid_location=(1, 1)),
                                    Key(steno="-UI", grid_location=(2, 1)),
                                    Key(steno="-AUIE", grid_location=(3, 1)),
                                    Key(steno="-AE", grid_location=(4, 1)),
                                    Key(steno="-O", label=num_bar_affected_label("O", "O<br /><small>9</small>"), grid_location=(0, 2)),
                                    Key(steno="-OI", grid_location=(1, 2)),
                                    Key(steno="-I", label=num_bar_affected_label("I<br /><small>+ O → A</small>", "I<br /><small>6</small>"), grid_location=(2, 2)),
                                    Key(steno="-IE", grid_location=(3, 2)),
                                    Key(steno="-E", label=num_bar_affected_label("E", "E<br /><small>3</small>"), grid_location=(4, 2)),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_LEFT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=Ref(0),
                                y=-middle_offset / 2,
    
                                elements=(
                                    Key(steno="-K", label=num_bar_affected_label("K<br /><small>+ Z → X</small>", "K<br /><small>?</small>"), height=reduced_key_height_small),
                                    Key(steno="-KJ", height=compound_key_size_small),
                                    Key(steno="-J", label=num_bar_affected_label("J<br /><small>+ L → H</small>", "J<br /><small>=</small>"), height=double_reduced_key_height_small),
                                    Key(steno="-JR", height=compound_key_size_small),
                                    Key(steno="-R", label=num_bar_affected_label("R<br /><small>+ N → M</small>", "R<br /><small>-</small>"), height=reduced_key_height + middle_offset / 2),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_LEFT,
                                organization=GroupOrganization.vertical(key_width),
    
                                x=key_width,
                                y=-ring_offset / 2,
    
                                elements=(
                                    Key(steno="-P", label=num_bar_affected_label("P<br /><small>+ J → B</small>", "P<br /><small>!</small>"), height=reduced_key_height_small),
                                    Key(steno="-PT", height=compound_key_size_small),
                                    Key(steno="-T", label=num_bar_affected_label("T<br /><small>+ J → D</small>", "T<br /><small>;</small>"), height=double_reduced_key_height_small),
                                    Key(steno="-TC", height=compound_key_size_small),
                                    Key(steno="-C", label=num_bar_affected_label("C<br /><small>+ J → G</small>", "C<br /><small>)</small>"), height=reduced_key_height + ring_offset / 2),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.BOTTOM_LEFT,
                                organization=GroupOrganization.grid(
                                    row_heights=pinky_row_heights,
                                    col_widths=(
                                        inner_end_column_width,
                                        end_column_compound_width,
                                        end_column_width,
                                    ),
                                ),
    
                                x=2 * key_width,
                                y=-pinky_offset / 2,
    
                                elements=(
                                    Key(steno="-F", label=num_bar_affected_label("F<br /><small>+ C → Q</small>", "F<br /><small>\"</small>"), grid_location=(0, 0)),
                                    Key(steno="-FS", grid_location=(1, 0)),
                                    Key(steno="-S", label=num_bar_affected_label("S", "S<br /><small>:</small>"), grid_location=(2, 0)),
                                    Key(steno="-FZ", grid_location=(0, 1)),
                                    Key(steno="-FSZ", grid_location=(1, 1)),
                                    Key(steno="-SZ", grid_location=(2, 1)),
                                    Key(steno="-Z", label=num_bar_affected_label("Z", "Z<br /><small>#</small>"), grid_location=(0, 2, 3, 1)),
                                ),
                            ),
                            KeyGroup(
                                alignment=GroupAlignment.TOP_LEFT,
                                organization=GroupOrganization.grid(
                                    row_heights=(palm_key_height,),
                                    col_widths=(palm_key_width,),
                                ),

                                x=1.5 * key_width,
                                y=2 * key_height,

                                elements=(
                                    Key(steno="_", label=num_bar_affected_label("NO SPACE", "NO SPACE<br /><small>BACKSPACE</small>"), grid_location=(0, 0)),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )