import qtpy
from arkitekt import App
from napari import Viewer
from qtpy import QtWidgets, QtCore


class BaseMikroNapariController(QtCore.QObject):
    app: App
    viewer: Viewer

    def __init__(
        self,
        *args,
        viewer: Viewer = None,
        app: App = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        assert viewer is not None, "viewer must be provided"
        assert app is not None, "app must be provided"
        self.app = app
        self.viewer = viewer
