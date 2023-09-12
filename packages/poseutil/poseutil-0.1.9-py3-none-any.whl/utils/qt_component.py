from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import *

def listViewSetup(list_widget, row, connect):
    for i in row:
        if ".DS_Store" in i:
            continue
        list_widget.addItem(i)
    list_widget.currentItemChanged.connect(connect)
    
def checkBoxSetup(checkBox, toolTip, toggle, connect):
    checkBox.setToolTip(toolTip)
    if toggle:
        checkBox.toggle()
    checkBox.stateChanged.connect(connect)


def labelSetup(label, move, title, fontSize = 15):
    label.move(move[0], move[1])
    label.setFont(QFont(title, fontSize))
    label.setText(title)
    label.show()

def sliderSetup(slider, label, move, range, step, defaultValue, connectData, val=1):
    slider.move(move[0], move[1])
    slider.setRange(range[0], range[1])
    slider.setSingleStep(step)
    slider.setValue(defaultValue)
    slider.valueChanged.connect(lambda: label.setText(str(round(slider.value() * val, 1))))
    slider.valueChanged.connect(connectData)
    slider.show()

def btnSetup(btn, toolTip, font, move, resize, connect):
    btn.setToolTip(toolTip)
    btn.setFont(font)
    btn.move(move[0], move[1])
    btn.resize(resize[0], resize[1])
    btn.clicked.connect(connect)

def btnSetting(btn, toolTip, font, clickedEvent):
    btn.setToolTip(toolTip)
    btn.setFont(font)
    btn.resize(btn.sizeHint())
    btn.clicked.connect(clickedEvent)

def tableSetup(table, rows, cols, data=None, row_header=None, col_header=None):
    table.setRowCount(rows)
    table.setColumnCount(cols)
    if row_header is not None:
        table.setHorizontalHeaderLabels(row_header)
    if col_header is not None:
        table.setVerticalHeaderLabels(col_header)
    if data is None: 
        return
    for idx, val in enumerate(data):
        if type(val) is list:
            for idx_2, val_2 in enumerate(val):
                item = QTableWidgetItem(str(val_2))
                table.setItem(idx_2, idx, item)
        else:
            item = QTableWidgetItem(val)
            table.setItem(idx, 0, item)
    table.resizeColumnsToContents()
    table.resizeRowsToContents()

def comboBoxSetup(combo_box, item_list, connect):
    for item in item_list:
        combo_box.addItem(item)
    combo_box.activated[str].connect(connect)