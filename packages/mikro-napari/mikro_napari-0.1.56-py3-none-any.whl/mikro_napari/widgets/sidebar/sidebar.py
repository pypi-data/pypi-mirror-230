import napari
from koil.qt import QtRunner
from mikro.api.schema import (
    ROIFragment,
    aexpand_roi,
    RepresentationFragment,
    TableFragment,
    get_table,
)
from qtpy import QtWidgets
from qtpy import QtCore
from arkitekt import App
from mikro_napari.utils import NapariROI
from napari.layers.image import Image
from mikro_napari.api.schema import (
    adetail_rep,
    DetailRepresentationFragment,
    DetailRepresentationFragmentOmeroPositions,
    DetailRepresentationFragmentOmeroTimepoints,
    DetailRepresentationFragmentMetrics,
)
import webbrowser
from mikro_napari.widgets.table.table_widget import TableWidget
from mikro_napari.widgets.base import BaseMikroNapariWidget


class RoiWidget(QtWidgets.QWidget):
    """A widget for displaying ROIs."""

    def __init__(self, app: App, roi: NapariROI, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)

        self.detailquery = QtRunner(aexpand_roi)
        self.detailquery.returned.connect(self.update_layout)
        self.detailquery.run(roi.id)

    def update_layout(self, roi: ROIFragment):
        self._layout.addWidget(QtWidgets.QLabel(roi.label))
        if roi.creator.email:
            self._layout.addWidget(QtWidgets.QLabel(roi.creator.email))
        self._layout.addWidget(QtWidgets.QLabel(roi.id))


class PositionWidget(QtWidgets.QWidget):
    def __init__(
        self, pos: DetailRepresentationFragmentOmeroPositions, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._layout = QtWidgets.QVBoxLayout()
        self.position = pos

        pos_label = QtWidgets.QPushButton(pos.name)
        pos_label.clicked.connect(self.pos_clicked)
        self._layout.addWidget(pos_label)
        self.setLayout(self._layout)

    def pos_clicked(self):
        webbrowser.open(
            f"http://localhost:6789/user/mikro/positions/{self.position.id}"
        )


class TimepointWidget(QtWidgets.QWidget):
    def __init__(
        self, timepoint: DetailRepresentationFragmentOmeroTimepoints, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._layout = QtWidgets.QVBoxLayout()
        self.timepoint = timepoint

        pos_label = QtWidgets.QPushButton(timepoint.name)
        pos_label.clicked.connect(self.pos_clicked)
        self._layout.addWidget(pos_label)
        self.setLayout(self._layout)

    def pos_clicked(self):
        webbrowser.open(
            f"http://localhost:6789/user/mikro/timepoints/{self.timepoint.id}"
        )


class MetricWidget(QtWidgets.QWidget):
    def __init__(
        self, metric: DetailRepresentationFragmentMetrics, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self._layout = QtWidgets.QVBoxLayout()
        self.metric = metric

        pos_label = QtWidgets.QPushButton(metric.key)
        pos_label.clicked.connect(self.pos_clicked)
        self._layout.addWidget(pos_label)

        pos_label = QtWidgets.QPushButton(str(metric.value))
        pos_label.clicked.connect(self.pos_clicked)
        self._layout.addWidget(pos_label)
        self.setLayout(self._layout)

    def pos_clicked(self):
        webbrowser.open(f"http://localhost:6789/user/mikro/timepoints/{self.metric.id}")


class RepresentationWidget(QtWidgets.QWidget):
    """A widget for displaying ROIs."""

    def __init__(self, image: RepresentationFragment, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.start_image = image
        print(self.start_image)
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)

        self.detailquery = QtRunner(adetail_rep)
        self.detailquery.returned.connect(self.update_layout)
        self.detailquery.run(image.id)

    def clearLayout(self):
        while self._layout.count():
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_layout(self, image: DetailRepresentationFragment):
        self.clearLayout()

        if image.name:
            self._layout.addWidget(QtWidgets.QLabel(image.name))

        if image.omero:
            for pos in image.omero.positions:
                self._layout.addWidget(PositionWidget(pos))

            for pos in image.omero.positions:
                self._layout.addWidget(TimepointWidget(pos))

        if image.metrics:
            for metric in image.metrics:
                self._layout.addWidget(MetricWidget(metric))


class SidebarWidget(BaseMikroNapariWidget):
    emit_image: QtCore.Signal = QtCore.Signal(object)

    def __init__(self, *args, **kwargs) -> None:
        super(SidebarWidget, self).__init__(*args, **kwargs)

        self.mylayout = QtWidgets.QVBoxLayout()

        self._active_widget = QtWidgets.QLabel("Nothing selected")
        self.mylayout.addWidget(self._active_widget)

        self.viewer.layers.selection.events.changed.connect(self.on_layer_changed)

        self.setLayout(self.mylayout)

    def show_table_widget(self, table: TableFragment):
        self.replace_widget(TableWidget(table, viewer=self.viewer, app=self.app))

    def replace_widget(self, widget):
        self.mylayout.removeWidget(self._active_widget)
        del self._active_widget
        self._active_widget = widget
        self.mylayout.addWidget(self._active_widget)

    def select_roi(self, roi: NapariROI):
        self.replace_widget(RoiWidget(self.app, roi))
        pass

    def on_layer_changed(self, event):
        self.viewer.layers.selection.active
        layer = self.viewer.layers.selection.active
        if layer is not None:
            if "representation" in layer.metadata:
                self.replace_widget(
                    RepresentationWidget(layer.metadata["representation"])
                )
                print(layer)
