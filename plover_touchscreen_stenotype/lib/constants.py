FONT_FAMILY = "Atkinson Hyperlegible, Segoe UI, Ubuntu"

# KeyWidget rule removes any native margin around KeyWidgets
KEY_GROUP_STYLESHEET = """
KeyGroupWidget {
    background: #00000000;
}

KeyWidget {
    background: #fdfdfd;
    border: 1px solid;
    border-color: #d0d0d0 #d0d0d0 #bababa #d0d0d0;
}

KeyWidget[matched_soft="true"] {
    background: #ca9e2e;
    border-color: #a36a2c #a36a2c #1f5153 #a36a2c;
}

KeyWidget[matched="true"] {
    background: #6f9f86;
    border-color: #2a6361 #2a6361 #1f5153 #2a6361;
}

KeyWidget[touched="true"] {
    background: #41796a;
}

KeyLabel[highlighted="true"] {
    color: #fff;
}
"""

GRAPHICS_VIEW_STYLE = "background: #00000000; border: none;"