# ============================================================
# E-WASTE AI - AUTOMATIC GROUPING
# ============================================================

GROUPING_RULES = {

    "reusable": [
        "connector",
        "display",
        "ic",
        "led",
        "potentiometer",
        "relay",
        "switch",
        "transformer",
        "transistor"
    ],

    "recyclable": [
        "battery",
        "button",
        "buzzer",
        "capacitor",
        "clock",
        "diode",
        "fuse",
        "heatsink",
        "inductor",
        "pads",
        "pins",
        "resistor"
    ],

    "pure_waste": [],

    "metal_bearing": [
        "battery",
        "button",
        "buzzer",
        "capacitor",
        "clock",
        "connector",
        "diode",
        "fuse",
        "heatsink",
        "ic",
        "inductor",
        "led",
        "pads",
        "pins",
        "potentiometer",
        "relay",
        "resistor",
        "switch",
        "transformer",
        "transistor"
    ]
}


def get_groups(component):

    groups = []

    for group, components in GROUPING_RULES.items():

        if component in components:
            groups.append(group)

    return groups