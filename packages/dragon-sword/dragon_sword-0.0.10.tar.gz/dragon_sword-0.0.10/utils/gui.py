from typing import List

from PyQt5.QtWidgets import QWidget, QBoxLayout, QHBoxLayout


def make_one_line(widgets: List[QWidget], box: QBoxLayout) -> QBoxLayout:
    inbox = QHBoxLayout()
    for item in widgets:
        inbox.addWidget(item)
    box.addLayout(inbox)
    return inbox


def highlight(widget: QWidget):
    widget.setStyleSheet("color:red")
    return widget
