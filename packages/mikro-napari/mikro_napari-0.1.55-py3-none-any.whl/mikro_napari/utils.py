from dataclasses import dataclass
from mikro.api.schema import ROIFragment, ROIType


@dataclass
class NapariROI:
    """A napari ROI."""

    type: str
    data: list
    color: str
    id: str


def convert_roi_to_napari_roi(roi: ROIFragment) -> NapariROI:
    """Convert a ROI to a napari ROI."""

    if roi.type in [
        ROIType.ELLIPSE,
        ROIType.RECTANGLE,
        ROIType.POLYGON,
        ROIType.LINE,
        ROIType.PATH,
    ]:
        return NapariROI(
            **{
                "type": roi.type.lower(),
                "data": roi.vector_data,
                "color": roi.creator.color or "white",
                "id": roi.id,
            }
        )

    return None
