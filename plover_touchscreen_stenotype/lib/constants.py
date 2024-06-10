FONT_FAMILY = "Atkinson Hyperlegible, Segoe UI, Ubuntu"

# KeyWidget rule removes any native margin around KeyWidgets
KEY_STYLESHEET = """
KeyWidget {
    background: #fdfdfd;
    border: 1px solid;
}

KeyWidget[matched="true"] {
    background: #6f9f86;
    color: #fff;
    border: 1px solid;
    border-color: #2a6361 #2a6361 #1f5153 #2a6361;
}

KeyWidget[touched="true"] {
    background: #41796a;
}
"""

GRAPHICS_VIEW_STYLE = "background: #00000000; border: none;"