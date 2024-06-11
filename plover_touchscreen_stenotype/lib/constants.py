FONT_FAMILY = "Atkinson Hyperlegible, Segoe UI, Ubuntu"

# KeyWidget rule removes any native margin around KeyWidgets
KEY_STYLESHEET = """
KeyWidget {
    background: #fdfdfd;
    border: 1px solid;
}

KeyWidget[matched_soft="true"] {
    background: #ca9e2e;
    color: #fff;
    border-color: #a36a2c #a36a2c #1f5153 #a36a2c;
}

KeyWidget[matched="true"] {
    background: #6f9f86;
    color: #fff;
    border-color: #2a6361 #2a6361 #1f5153 #2a6361;
}

KeyWidget[touched="true"] {
    background: #41796a;
}
"""

GRAPHICS_VIEW_STYLE = "background: #00000000; border: none;"

KEY_CONTAINER_STYLE = "background: #00000000;"