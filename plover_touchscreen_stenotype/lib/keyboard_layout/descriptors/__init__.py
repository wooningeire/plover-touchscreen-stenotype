from . import (
    english_stenotype_ireland,
    english_stenotype_lapwing,
    english_stenotype_amphitheory,
    english_velotype
)

DEFAULT_KEYBOARD_LAYOUT_NAME = "English stenotype (Lapwing)"

KEYBOARD_LAYOUT_BUILDERS = {
    "English stenotype (Ireland)": english_stenotype_ireland.build_layout_descriptor,
    # "English stenotype (Ireland extended)": english_stenotype_lapwing.build_layout_descriptor,
    "English stenotype (Lapwing)": english_stenotype_lapwing.build_layout_descriptor,
    "English stenotype (Amphitheory)": english_stenotype_amphitheory.build_layout_descriptor,
    "English velotype": english_velotype.build_layout_descriptor,
    # "English palantype": english_stenotype_amphitheory.build_layout_descriptor,
}