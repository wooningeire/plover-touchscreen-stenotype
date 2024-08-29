from . import (
    english_stenotype,
    english_stenotype_extended_custom
)

DEFAULT_KEYBOARD_LAYOUT_NAME = "English (Lapwing)"

KEYBOARD_LAYOUT_BUILDERS = {
    "English (Lapwing)": english_stenotype.build_layout_descriptor,
    "English (Amphitheory)": english_stenotype_extended_custom.build_layout_descriptor,
}