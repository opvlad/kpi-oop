import json

from PySide6.QtWidgets import QInputDialog


def ask_group(parent_window) -> None:
    with open("fiot_groups.json", "r") as file:
        fiot_groups = json.load(file)

    group, ok = QInputDialog.getItem(
        parent_window,
        "Select group",
        "label",
        fiot_groups,
        editable=False
    )
    if ok:
        parent_window.data_label.setText(group)
