import pandas as pd
from mikro.api.schema import TableFragment
from qtpy.QtWidgets import QTableView, QApplication
from qtpy.QtCore import QAbstractTableModel, Qt, QModelIndex
from qtpy import QtWidgets, QtCore
import napari
from arkitekt import App
from mikro_napari.widgets.base import BaseMikroNapariWidget
from .dataframe import PandasModel


class TableWidget(BaseMikroNapariWidget):
    emit_image: QtCore.Signal = QtCore.Signal(object)

    def __init__(self, table: TableFragment, *args, **kwargs) -> None:
        super(TableWidget, self).__init__(*args, **kwargs)
        self.view = QTableView()
        self.view.horizontalHeader().setStretchLastSection(False)
        self.view.setAlternatingRowColors(False)
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setWindowTitle(table.name)

        self.model = PandasModel(table.data, parent=self)
        self.view.setModel(self.model)
        self.view.show()

        self.mylayout = QtWidgets.QVBoxLayout()
        self.mylayout.addWidget(self.view)

        self.setLayout(self.mylayout)

    def replace_widget(self, widget):
        self.mylayout.removeWidget(self._active_widget)
        del self._active_widget
        self._active_widget = widget
        self.mylayout.addWidget(self._active_widget)
