import asyncio
import math
import uuid
from typing import Dict, List, Optional
from arkitekt import App
import dask.array as da
import napari
import numpy as np
from napari.layers.shapes._shapes_constants import Mode
from qtpy import QtCore, QtWidgets
from koil.qt import QtCoro, QtFuture, QtGenerator, QtGeneratorRunner, QtRunner, QtSignal
from mikro.api.schema import (
    Create_roiMutation,
    FeatureFragment,
    InputVector,
    LabelFragment,
    ListROIFragment,
    MetricFragment,
    OmeroFragmentPhysicalsize,
    PositionFragment,
    RepresentationFragment,
    RepresentationVariety,
    ROIFragment,
    RoiTypeInput,
    StageFragment,
    Watch_roisSubscriptionRois,
    acreate_roi,
    aget_rois,
    awatch_rois,
    get_representation,
)
from mikro_napari.api.schema import (
    Delete_roiMutationDeleteroi,
    DetailLabelFragment,
    adelete_roi,
    aget_label_for,
    delete_roi,
    get_image_stage,
)
from mikro_napari.utils import NapariROI, convert_roi_to_napari_roi
from rath.scalars import ID

DESIGN_MODE_MAP = {
    Mode.ADD_RECTANGLE: RoiTypeInput.RECTANGLE,
    Mode.ADD_ELLIPSE: RoiTypeInput.ELLIPSIS,
    Mode.ADD_LINE: RoiTypeInput.LINE,
}

SELECT_MODE_MAP = {
    Mode.DIRECT: "direct",
}


DOUBLE_CLICK_MODE_MAP = {
    Mode.ADD_POLYGON: RoiTypeInput.POLYGON,
    Mode.ADD_PATH: RoiTypeInput.PATH,
}


def top_left_in_view(
    position: PositionFragment,
    image: RepresentationFragment,
    physical_size: OmeroFragmentPhysicalsize,
):
    """Caluclate the top left corner of the image in world coordinates.

    Args:
        position (Position): _description_
        image (Representation): _description_
        physical_size (RepresentationFragmentOmeroPhysicalsize): _description_
    """

    return (
        np.array(
            (
                position.z / physical_size.x - (image.data.sizes["z"] / 2),
                position.y / physical_size.y - (image.data.sizes["y"] / 2),
                position.x / physical_size.z - (image.data.sizes["x"] / 2),
            )
        ),
        np.array((image.data.sizes["z"], image.data.sizes["y"], image.data.sizes["x"])),
        image.data,
    )


class AskForRoi(QtWidgets.QWidget):
    def __init__(
        self,
        controller,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.button = QtWidgets.QPushButton("All Rois Marked")
        self.button.clicked.connect(self.on_done)
        self.mylayout = controller.widget.mylayout

    def ask(self, qt_generator):
        self.qt_generator = qt_generator
        self.mylayout.addWidget(self.button)
        self.mylayout.update()

    def on_done(self) -> None:
        self.qt_generator.stop()
        self.mylayout.removeWidget(self.button)
        self.button.setParent(None)
        self.mylayout.update()


class TaskDone(QtWidgets.QWidget):
    def __init__(
        self,
        controller,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.mylayout = QtWidgets.QHBoxLayout()
        controller.widget.mylayout.addLayout(self.mylayout)
        self.listeners = {}
        self.buttons = {}
        self.futures = {}
        self.ask_coro = QtCoro(self.ask)
        self.ask_coro.cancelled.connect(self.on_cancelled)

    def ask(self, future: QtFuture, text):
        button = QtWidgets.QPushButton(text)
        button.clicked.connect(lambda: self.on_done(future))
        self.futures[future.id] = future
        self.buttons[future.id] = button
        self.update_buttons()

    def on_done(self, future) -> None:
        future.resolve(True)
        del self.buttons[future.id]
        self.update_buttons()

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_buttons(self):
        self.clearLayout(self.mylayout)
        for button in self.buttons.values():
            self.mylayout.addWidget(button)

        self.mylayout.update()

    def on_cancelled(self, future):
        del self.buttons[future.id]
        self.update_buttons()


class ManagedLayer(QtCore.QObject):
    def __init__(self, *args, viewer: napari.Viewer = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert viewer is not None, "Managed Layer needs access to the viewer"
        self.viewer = viewer
        self.managed_layers = {}

    def add_layer(self, layerid: str, layer: "ManagedLayer"):
        self.managed_layers[layerid] = layer

    def remove_layer(self, layerid: str):
        self.managed_layers.pop(layerid)

    def on_destroy(self):
        pass

    def destroy(self):
        for layer in self.managed_layers.values():
            layer.destroy()

        self.on_destroy()


class RoiLayer(ManagedLayer):
    roi_user_created = QtCore.Signal(ROIFragment)
    roi_user_deleted = QtCore.Signal(str)
    roi_user_updated = QtCore.Signal(ROIFragment)
    rois_user_selected = QtCore.Signal(list)
    roi_event_created = QtCore.Signal(ListROIFragment)
    roi_event_deleted = QtCore.Signal(str)
    roi_event_updated = QtCore.Signal(ListROIFragment)

    def __init__(
        self,
        image: RepresentationFragment,
        scale_to_physical_size: bool = True,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.image = image
        self.get_rois_query = QtRunner(aget_rois)
        self.get_rois_query.returned.connect(self._on_rois_loaded)
        self.get_rois_query.errored.connect(print)

        self.create_rois_runner = QtRunner(acreate_roi)
        self.create_rois_runner.returned.connect(self.on_roi_created)
        self.create_rois_runner.errored.connect(print)

        self.delete_rois_runner = QtRunner(adelete_roi)
        self.delete_rois_runner.returned.connect(self.on_roi_deleted)
        self.delete_rois_runner.errored.connect(print)

        self.watch_rois_subscription = QtGeneratorRunner(awatch_rois)
        self.watch_rois_subscription.yielded.connect(self.on_rois_updated)
        self.watch_rois_subscription.errored.connect(print)

        self.scale_to_physical_size = scale_to_physical_size
        self.koiled_create_rois = QtSignal(self.create_rois_runner.returned)

        self.layer = None
        self._get_rois_future = None
        self.is_watching = False
        self._watch_rois_future = None
        self._napari_rois: List[NapariROI] = []
        self._roi_layer = None
        self.roi_state = {}

    def on_destroy(self):
        self.viewer.remove_layer(self.layer)
        if self._get_rois_future is not None and not self._get_rois_future.done():
            self._get_rois_future.cancel()
        if self._watch_rois_future is not None and not self._watch_rois_future.done():
            self._watch_rois_future.cancel()

    def show(self, fetch_rois=True, watch_rois=True):
        self._roi_layer = self.viewer.add_shapes()
        self._roi_layer.mouse_drag_callbacks.append(self.on_drag_roi_layer)
        self._roi_layer.mouse_double_click_callbacks.append(
            self.on_double_click_roi_layer
        )
        if fetch_rois:
            self.show_rois()

        if watch_rois:
            self.watch_rois()

    def on_roi_deleted(self, result: Delete_roiMutationDeleteroi):
        if not self.is_watching:
            del self.roi_state[str(result.id)]

        self.roi_user_deleted.emit(str(result.id))

    def on_roi_created(self, result: ROIFragment):
        if not self.is_watching:
            self.roi_state[result.id] = result

        self.roi_user_created.emit(result)

    def show_rois(self):
        self._get_rois_future = self.get_rois_query.run(representation=self.image.id)

    def watch_rois(self):
        self.is_watching = True
        self._watch_rois_future = self.watch_rois_subscription.run(
            representation=self.image.id
        )

    def update_roi_layer(self):
        self._napari_rois: List[NapariROI] = list(
            filter(
                lambda x: x is not None,
                [convert_roi_to_napari_roi(roi) for roi in self.roi_state.values()],
            )
        )
        self._roi_layer.name = f"ROIs for {self.image.name}"
        self._roi_layer.data = []

        for i in self._napari_rois:
            self._roi_layer.add(
                i.data,
                shape_type=i.type,
                edge_width=1,
                edge_color="white",
                face_color=i.color,
            )

        self._roi_layer.features = {"roi": [r.id for r in self._napari_rois]}

    def _on_rois_loaded(self, rois: List[ListROIFragment]):
        self.roi_state = {roi.id: roi for roi in rois}
        self.update_roi_layer()

    def on_rois_updated(self, ev: Watch_roisSubscriptionRois):
        if ev.create:
            self.roi_state[ev.create.id] = ev.create
            self.roi_event_created.emit(ev.create)

        if ev.delete:
            del self.roi_state[ev.delete]
            self.roi_event_deleted.emit(str(ev.delete))

        self.update_roi_layer()

    def on_drag_roi_layer(self, layer, event):
        while event.type != "mouse_release":
            yield

        print("dragged")
        if layer.mode in SELECT_MODE_MAP:
            print(self._roi_layer.selected_data)
            selected_rois = []
            for i in self._roi_layer.selected_data:
                napari_roi = self._napari_rois[i]
                selected_rois.append(self.roi_state[napari_roi.id])

            self.rois_user_selected.emit(selected_rois)

        if layer.mode in DESIGN_MODE_MAP:
            if len(self._roi_layer.data) > len(self._napari_rois):
                c, t, z = event.position[:3]
                print("Creating")

                self.create_rois_runner.run(
                    representation=self.image.id,
                    vectors=InputVector.list_from_numpyarray(
                        self._roi_layer.data[-1], t=t, z=z, c=c
                    ),
                    type=DESIGN_MODE_MAP[layer.mode],
                )

        if len(self._roi_layer.data) < len(self._napari_rois):
            if "roi" in self._roi_layer.features:
                there_rois = set([f for f in self._roi_layer.features["roi"]])
                state_rois = set([f.id for f in self._napari_rois])
                difference_rois = state_rois - there_rois
                for roi_id in difference_rois:
                    self.delete_rois_runner.run(roi_id)

    def on_double_click_roi_layer(self, layer, event):
        print("double clicked")
        if layer.mode in DOUBLE_CLICK_MODE_MAP:
            if len(self._roi_layer.data) > len(self._napari_rois):
                t, z, c = event.position[:3]

                self.create_rois_runner.run(
                    representation=self.image.id,
                    vectors=InputVector.list_from_numpyarray(
                        self._roi_layer.data[-1], t=t, z=z, c=c
                    ),
                    type=DOUBLE_CLICK_MODE_MAP[layer.mode],
                )


class ImageLayer(ManagedLayer):
    on_rep_layer_clicked = QtCore.Signal(RepresentationFragment)

    def __init__(
        self,
        image: RepresentationFragment,
        scale_to_physical_size: bool = False,
        with_rois=True,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.managed_image = image
        self._image_layer = None
        self.with_rois = with_rois
        self.scale_to_physical_size = scale_to_physical_size
        self.roi_layer = None

    def on_destroy(self):
        self.viewer.remove_layer(self._image_layer)

    def show(self, respect_physical_size=False):
        if respect_physical_size:
            raise NotImplementedError

        scale = None

        if (
            self.managed_image.omero
            and self.managed_image.omero.physical_size
            and self.scale_to_physical_size
        ):
            scale = self.managed_image.omero.physical_size.to_scale()
            pass

        if self.managed_image.variety == RepresentationVariety.RGB:
            self._image_layer = self.viewer.add_image(
                self.managed_image.data.transpose(*list("tzyxc")),
                metadata={
                    "mikro": True,
                    "representation": self.managed_image,
                    "type": "IMAGE",
                },
                scale=scale,
            )
        else:
            self._image_layer = self.viewer.add_image(
                self.managed_image.data.transpose(*list("ctzyx")),
                metadata={
                    "mikro": True,
                    "representation": self.managed_image,
                    "type": "IMAGE",
                },
                scale=scale,
            )

        print(scale)


class RepresentationQtModel(QtCore.QObject):
    rep_changed = QtCore.Signal(RepresentationFragment)

    def __init__(self, widget, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.widget = widget
        self.app: App = self.widget.app
        self.viewer: napari.Viewer = self.widget.viewer

        self.managed_layers: Dict[str, ImageLayer] = {}
        self.managed_roi_layers: Dict[str, RoiLayer] = {}

        self.ask_roi_dialog = AskForRoi(self)
        self.task_done_dialog = TaskDone(self)

        self._image_layer = None
        self._roi_layer = None
        self.roi_state: Dict[str, ListROIFragment] = {}

        self.create_image_layer_coro = QtCoro(self.create_image_layer, autoresolve=True)
        self.create_roi_layer_coro = QtCoro(self.create_roi_layer, autoresolve=True)

    def create_image_layer(
        self, image: RepresentationFragment, scale_to_physical_size: bool = True
    ) -> ImageLayer:
        if image.id not in self.managed_layers:
            layer = ImageLayer(
                image, viewer=self.viewer, scale_to_physical_size=scale_to_physical_size
            )
            self.managed_layers[image.id] = layer
        else:  # pragma: no cover
            layer = self.managed_layers[image.id]

        layer.show()
        return layer

    def create_roi_layer(
        self,
        image: RepresentationFragment,
        scale_to_physical_size: bool = True,
        fetch_rois=True,
        watch_rois=True,
    ) -> RoiLayer:
        if image.id not in self.managed_roi_layers:
            layer = RoiLayer(
                image, viewer=self.viewer, scale_to_physical_size=scale_to_physical_size
            )
            self.managed_roi_layers[image.id] = layer
        else:  # pragma: no cover
            layer = self.managed_roi_layers[image.id]

        layer.show(fetch_rois=fetch_rois, watch_rois=watch_rois)
        return layer

    def on_image_loaded(
        self,
        rep: RepresentationFragment,
        show_roi_layer: bool = True,
        scale_to_physical_size: bool = True,
    ):
        """Show on Napari

        Loads the image into the viewer

        Args:
            rep (RepresentationFragment): The Image
        """
        self.create_image_layer(rep, scale_to_physical_size=scale_to_physical_size)
        if show_roi_layer:
            self.create_roi_layer(rep)

    def open_metric(self, metric: MetricFragment):
        """Open a metric

        Loads the metric into the viewer

        Args:
            rep (RepresentationFragment): The Image
        """
        self.active_representation = get_representation(metric.rep.id)

    def open_label(self, label: LabelFragment):
        """Show Label

        Loads the label and its corresponding image into the viewer, highlighting the active
        label in a different color, but showing all labels

        Args:
            label (RepresentationFragment): The label to show
        """
        self.active_representation = get_representation(label.representation.id)

    def open_feature(self, rep: FeatureFragment):
        """Open Feature

        Loads the feature into the viewer

        Args:
            rep (RepresentationFragment): The Image
        """
        self.active_representation = get_representation(rep.label.representation.id)

    def open_position(self, pos: PositionFragment):
        """Open Position

        Loads the position into the viewer as a time series

        Args:
            rep (RepresentationFragment): The Image

        """

        reps = [omero.representation.data for omero in pos.omeros]

        image = da.stack([rep.data for rep in reps], axis=1)

        self.viewer.add_image(
            image,
            name="Position {pos.x}, {pos.y}, {pos.z}",
            metadata={"mikro": True, "type": "POSITION"},
        )

    def open_stage(self, acq: StageFragment, limit_t: int = 2):
        """Open Stage

        Loads the stage into the viewer


        Args:
            rep (RepresentationFragment): The Image

        """
        t_limit = 1
        stage = get_image_stage(acq.id, limit=t_limit)

        # assert correct pixelsize
        physical_size = stage.positions[0].omeros[0].physical_size

        stage_positions = []
        view_datas = []
        view_shapes = []

        for p in stage.positions:
            for t in p.omeros:
                assert physical_size.is_similar(t.physical_size, tolerance=0.003)
                view_position, image_shape, view_data = top_left_in_view(
                    p, t.representation, physical_size
                )
                stage_positions.append(view_position)
                view_shapes.append(image_shape)
                view_datas.append(view_data)

        print(stage_positions)

        offset = np.array(stage_positions)
        shapes = np.array(view_shapes)

        offset_min = offset.min(axis=0)
        x_max = offset.max(axis=0)

        # rescale positions to fit in view
        top_left_offsets = offset - offset_min
        bottom_right_offsets = top_left_offsets + shapes

        print(top_left_offsets)
        print(bottom_right_offsets)

        bottom_right_max = bottom_right_offsets.max(axis=0)
        bottom_right_max_ceiling = np.ceil(bottom_right_max).astype(int)

        xmax = np.max([p.x for p in stage.positions]) or 1
        ymax = np.max([p.y for p in stage.positions]) or 1
        zmax = np.max([p.z for p in stage.positions]) or 1

        image = da.zeros(
            (
                1,
                t_limit,
                bottom_right_max_ceiling[0],
                bottom_right_max_ceiling[1],
                bottom_right_max_ceiling[2],
            )
        )
        for i, view_data in enumerate(view_datas):
            x = view_data.sel(t=0, c=0)

            z1 = math.floor(top_left_offsets[i][0])
            y1 = math.floor(top_left_offsets[i][1])
            x1 = math.floor(top_left_offsets[i][2])

            z2 = z1 + x.sizes["z"]
            y2 = y1 + x.sizes["y"]
            x2 = x1 + x.sizes["x"]

            print(z1, z2, y1, y2, x1, x2)

            image[
                0,
                0,
                z1:z2,
                y1:y2,
                x1:x2,
            ] = x.data
        image = image.compute()

        self.viewer.add_image(
            image,
            name="Position {pos.x}, {pos.y}, {pos.z}",
            metadata={"mikro": True, "type": "POSITION"},
        )

    def tile_images(self, reps: List[RepresentationFragment]):
        """Tile Images on Napari

        Loads the images and tiles them into the viewer

        Args:
            reps (List[RepresentationFragment]): The Image
        """

        shape_array = np.array([np.array(rep.data.shape[:4]) for rep in reps])
        max_shape = np.max(shape_array, axis=0)

        cdata = []
        for rep in reps:
            data = da.zeros(list(max_shape) + [rep.data.shape[4]])
            data[
                : rep.data.shape[0],
                : rep.data.shape[1],
                : rep.data.shape[2],
                : rep.data.shape[3],
                :,
            ] = rep.data
            cdata.append(data)

        x = da.concatenate(cdata, axis=-1).squeeze()
        name = " ".join([rep.name for rep in reps])

        self.viewer.add_image(
            x,
            name=name,
            metadata={"mikro": True, "type": "IMAGE"},
            scale=reps[0].omero.scale if reps[0].omero else None,
        )

    async def stream_rois(
        self, rep: RepresentationFragment, show_old_rois=False
    ) -> ROIFragment:
        """Stream ROIs

        Asks the user to mark rois on the image, once user deams done, the rois are returned

        Args:
            rep (RepresentationFragment): The Image
            show_old_rois (bool, optional): Show already marked rois. Defaults to False.

        Returns:
            rois (List[RoiFragment]): The Image
        """
        layer = await self.create_image_layer_coro.acall(rep)
        roilayer = await self.create_roi_layer_coro.acall(rep, fetch_rois=show_old_rois)

        create_listener = roilayer.koiled_create_rois
        stop_task = asyncio.create_task(
            self.task_done_dialog.ask_coro.acall("All rois marked?")
        )
        try:
            while True:
                x = asyncio.create_task(create_listener.aonce())

                done, pending = await asyncio.wait(
                    [x, stop_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for i in done:
                    if i == stop_task:
                        for p in pending:
                            p.cancel()
                        try:
                            await asyncio.gather(*pending)
                        except asyncio.CancelledError:
                            print("Cancelled")
                            pass
                        return
                    else:
                        roi = i.result()
                        yield roi

        except asyncio.CancelledError:
            print("Cancelled")
            if not stop_task.done():
                stop_task.cancel()

            if not x.done():
                x.cancel()

            try:
                await asyncio.gather(stop_task, x)
            except asyncio.CancelledError:
                print("Cancelled")
                pass

    def on_label_loaded(self, label: DetailLabelFragment):
        """Shows beauitful Images

        Loads the image into the viewer

        Args:
            rep (RepresentationFragment): The Image
        """
        print("This is the label", label)

    def on_rois_loaded(self, rois: List[ListROIFragment]):
        self.roi_state = {roi.id: roi for roi in rois}
        self.update_roi_layer()

    def on_rois_updated(self, ev: Watch_roisSubscriptionRois):
        if ev.create:
            self.roi_state[ev.create.id] = ev.create
            if self.stream_roi_generator:
                self.stream_roi_generator.next(ev.create)

        if ev.delete:
            del self.roi_state[ev.delete]

        self.update_roi_layer()

    def on_drag_image_layer(self, layer, event):
        while event.type != "mouse_release":
            yield

        print("Fired")
        print(self.active_representation.variety)
        if self.active_representation.variety == RepresentationVariety.MASK:
            if self._getlabeltask and not self._getlabeltask.done():
                self._getlabeltask.cancel(wait=True)

            value = layer.get_value(event.position)
            print(value)
            if value:
                self._getlabeltask = self.get_label_query.run(
                    representation=self.active_representation.id, instance=int(value)
                )

    def on_drag_roi_layer(self, layer, event):
        while event.type != "mouse_release":
            yield

        if layer.mode in SELECT_MODE_MAP:
            print(self._roi_layer.selected_data)
            for i in self._roi_layer.selected_data:
                napari_roi = self._napari_rois[i]
                self.viewer.window.sidebar.select_roi(napari_roi)

        if layer.mode in DESIGN_MODE_MAP:
            if len(self._roi_layer.data) > len(self._napari_rois):
                c, t, z = event.position[:3]

                self.create_rois_runner.run(
                    representation=self._active_representation.id,
                    vectors=InputVector.list_from_numpyarray(
                        self._roi_layer.data[-1], t=t, z=z, c=c
                    ),
                    type=DESIGN_MODE_MAP[layer.mode],
                )

        if len(self._roi_layer.data) < len(self._napari_rois):
            there_rois = set([f for f in self._roi_layer.features["roi"]])
            state_rois = set([f.id for f in self._napari_rois])
            difference_rois = state_rois - there_rois
            for roi_id in difference_rois:
                delete_roi(roi_id)

    def on_double_click_roi_layer(self, layer, event):
        print("Fired")
        print(self._roi_layer.features)
        if layer.mode in DOUBLE_CLICK_MODE_MAP:
            if len(self._roi_layer.data) > len(self._napari_rois):
                t, z, c = event.position[:3]

                self.create_rois_runner.run(
                    representation=self._active_representation.id,
                    vectors=InputVector.list_from_numpyarray(
                        self._roi_layer.data[-1], t=t, z=z, c=c
                    ),
                    type=DOUBLE_CLICK_MODE_MAP[layer.mode],
                )

    def print(self, *args, **kwargs):
        print(*args, **kwargs)

    def update_roi_layer(self):
        if not self._roi_layer:
            self._roi_layer = self.viewer.add_shapes(
                metadata={
                    "mikro": True,
                    "type": "ROIS",
                    "representation": self._active_representation,
                }
            )
            self._roi_layer.mouse_drag_callbacks.append(self.on_drag_roi_layer)
            self._roi_layer.mouse_double_click_callbacks.append(
                self.on_double_click_roi_layer
            )

        self._napari_rois: List[NapariROI] = list(
            filter(
                lambda x: x is not None,
                [convert_roi_to_napari_roi(roi) for roi in self.roi_state.values()],
            )
        )

        self._roi_layer.data = []
        self._roi_layer.name = f"ROIs for {self._active_representation.name}"

        for i in self._napari_rois:
            self._roi_layer.add(
                i.data,
                shape_type=i.type,
                edge_width=1,
                edge_color="white",
                face_color=i.color,
            )

        self._roi_layer.features = {"roi": [r.id for r in self._napari_rois]}
