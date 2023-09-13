from typing import Literal, Iterator, List, Dict, Optional, AsyncIterator, Tuple
from datetime import datetime
from mikro.rath import MikroRath
from mikro.funcs import asubscribe, execute, aexecute, subscribe
from mikro.traits import (
    Stage,
    ROI,
    PhysicalSize,
    Representation,
    Vectorizable,
    Position,
    Omero,
)
from mikro.scalars import Store, MetricValue, FeatureValue, AffineMatrix, AssignationID
from pydantic import BaseModel, Field
from rath.scalars import ID
from enum import Enum


class CommentableModels(str, Enum):
    GRUNNLAG_USERMETA = "GRUNNLAG_USERMETA"
    GRUNNLAG_ANTIBODY = "GRUNNLAG_ANTIBODY"
    GRUNNLAG_OBJECTIVE = "GRUNNLAG_OBJECTIVE"
    GRUNNLAG_CAMERA = "GRUNNLAG_CAMERA"
    GRUNNLAG_INSTRUMENT = "GRUNNLAG_INSTRUMENT"
    GRUNNLAG_DATASET = "GRUNNLAG_DATASET"
    GRUNNLAG_EXPERIMENT = "GRUNNLAG_EXPERIMENT"
    GRUNNLAG_CONTEXT = "GRUNNLAG_CONTEXT"
    GRUNNLAG_RELATION = "GRUNNLAG_RELATION"
    GRUNNLAG_DATALINK = "GRUNNLAG_DATALINK"
    GRUNNLAG_EXPERIMENTALGROUP = "GRUNNLAG_EXPERIMENTALGROUP"
    GRUNNLAG_ANIMAL = "GRUNNLAG_ANIMAL"
    GRUNNLAG_OMEROFILE = "GRUNNLAG_OMEROFILE"
    GRUNNLAG_MODEL = "GRUNNLAG_MODEL"
    GRUNNLAG_SAMPLE = "GRUNNLAG_SAMPLE"
    GRUNNLAG_STAGE = "GRUNNLAG_STAGE"
    GRUNNLAG_CHANNEL = "GRUNNLAG_CHANNEL"
    GRUNNLAG_POSITION = "GRUNNLAG_POSITION"
    GRUNNLAG_ERA = "GRUNNLAG_ERA"
    GRUNNLAG_TIMEPOINT = "GRUNNLAG_TIMEPOINT"
    GRUNNLAG_REPRESENTATION = "GRUNNLAG_REPRESENTATION"
    GRUNNLAG_OMERO = "GRUNNLAG_OMERO"
    GRUNNLAG_DIMENSIONMAP = "GRUNNLAG_DIMENSIONMAP"
    GRUNNLAG_VIEW = "GRUNNLAG_VIEW"
    GRUNNLAG_METRIC = "GRUNNLAG_METRIC"
    GRUNNLAG_THUMBNAIL = "GRUNNLAG_THUMBNAIL"
    GRUNNLAG_VIDEO = "GRUNNLAG_VIDEO"
    GRUNNLAG_ROI = "GRUNNLAG_ROI"
    GRUNNLAG_LABEL = "GRUNNLAG_LABEL"
    GRUNNLAG_FEATURE = "GRUNNLAG_FEATURE"
    BORD_TABLE = "BORD_TABLE"
    BORD_GRAPH = "BORD_GRAPH"


class SharableModels(str, Enum):
    """Sharable Models are models that can be shared amongst users and groups. They representent the models of the DB"""

    GRUNNLAG_USERMETA = "GRUNNLAG_USERMETA"
    GRUNNLAG_ANTIBODY = "GRUNNLAG_ANTIBODY"
    GRUNNLAG_OBJECTIVE = "GRUNNLAG_OBJECTIVE"
    GRUNNLAG_CAMERA = "GRUNNLAG_CAMERA"
    GRUNNLAG_INSTRUMENT = "GRUNNLAG_INSTRUMENT"
    GRUNNLAG_DATASET = "GRUNNLAG_DATASET"
    GRUNNLAG_EXPERIMENT = "GRUNNLAG_EXPERIMENT"
    GRUNNLAG_CONTEXT = "GRUNNLAG_CONTEXT"
    GRUNNLAG_RELATION = "GRUNNLAG_RELATION"
    GRUNNLAG_DATALINK = "GRUNNLAG_DATALINK"
    GRUNNLAG_EXPERIMENTALGROUP = "GRUNNLAG_EXPERIMENTALGROUP"
    GRUNNLAG_ANIMAL = "GRUNNLAG_ANIMAL"
    GRUNNLAG_OMEROFILE = "GRUNNLAG_OMEROFILE"
    GRUNNLAG_MODEL = "GRUNNLAG_MODEL"
    GRUNNLAG_SAMPLE = "GRUNNLAG_SAMPLE"
    GRUNNLAG_STAGE = "GRUNNLAG_STAGE"
    GRUNNLAG_CHANNEL = "GRUNNLAG_CHANNEL"
    GRUNNLAG_POSITION = "GRUNNLAG_POSITION"
    GRUNNLAG_ERA = "GRUNNLAG_ERA"
    GRUNNLAG_TIMEPOINT = "GRUNNLAG_TIMEPOINT"
    GRUNNLAG_REPRESENTATION = "GRUNNLAG_REPRESENTATION"
    GRUNNLAG_OMERO = "GRUNNLAG_OMERO"
    GRUNNLAG_DIMENSIONMAP = "GRUNNLAG_DIMENSIONMAP"
    GRUNNLAG_VIEW = "GRUNNLAG_VIEW"
    GRUNNLAG_METRIC = "GRUNNLAG_METRIC"
    GRUNNLAG_THUMBNAIL = "GRUNNLAG_THUMBNAIL"
    GRUNNLAG_VIDEO = "GRUNNLAG_VIDEO"
    GRUNNLAG_ROI = "GRUNNLAG_ROI"
    GRUNNLAG_LABEL = "GRUNNLAG_LABEL"
    GRUNNLAG_FEATURE = "GRUNNLAG_FEATURE"
    BORD_TABLE = "BORD_TABLE"
    BORD_GRAPH = "BORD_GRAPH"


class LokClientGrantType(str, Enum):
    """An enumeration."""

    CLIENT_CREDENTIALS = "CLIENT_CREDENTIALS"
    "Backend (Client Credentials)"
    IMPLICIT = "IMPLICIT"
    "Implicit Grant"
    AUTHORIZATION_CODE = "AUTHORIZATION_CODE"
    "Authorization Code"
    PASSWORD = "PASSWORD"
    "Password"
    SESSION = "SESSION"
    "Django Session"


class LinkableModels(str, Enum):
    """LinkableModels Models are models that can be shared amongst users and groups. They representent the models of the DB"""

    ADMIN_LOGENTRY = "ADMIN_LOGENTRY"
    AUTH_PERMISSION = "AUTH_PERMISSION"
    AUTH_GROUP = "AUTH_GROUP"
    CONTENTTYPES_CONTENTTYPE = "CONTENTTYPES_CONTENTTYPE"
    SESSIONS_SESSION = "SESSIONS_SESSION"
    TAGGIT_TAG = "TAGGIT_TAG"
    TAGGIT_TAGGEDITEM = "TAGGIT_TAGGEDITEM"
    KOMMENT_COMMENT = "KOMMENT_COMMENT"
    DB_TESTMODEL = "DB_TESTMODEL"
    LOK_LOKUSER = "LOK_LOKUSER"
    LOK_LOKAPP = "LOK_LOKAPP"
    LOK_LOKCLIENT = "LOK_LOKCLIENT"
    GUARDIAN_USEROBJECTPERMISSION = "GUARDIAN_USEROBJECTPERMISSION"
    GUARDIAN_GROUPOBJECTPERMISSION = "GUARDIAN_GROUPOBJECTPERMISSION"
    GRUNNLAG_USERMETA = "GRUNNLAG_USERMETA"
    GRUNNLAG_ANTIBODY = "GRUNNLAG_ANTIBODY"
    GRUNNLAG_OBJECTIVE = "GRUNNLAG_OBJECTIVE"
    GRUNNLAG_CAMERA = "GRUNNLAG_CAMERA"
    GRUNNLAG_INSTRUMENT = "GRUNNLAG_INSTRUMENT"
    GRUNNLAG_DATASET = "GRUNNLAG_DATASET"
    GRUNNLAG_EXPERIMENT = "GRUNNLAG_EXPERIMENT"
    GRUNNLAG_CONTEXT = "GRUNNLAG_CONTEXT"
    GRUNNLAG_RELATION = "GRUNNLAG_RELATION"
    GRUNNLAG_DATALINK = "GRUNNLAG_DATALINK"
    GRUNNLAG_EXPERIMENTALGROUP = "GRUNNLAG_EXPERIMENTALGROUP"
    GRUNNLAG_ANIMAL = "GRUNNLAG_ANIMAL"
    GRUNNLAG_OMEROFILE = "GRUNNLAG_OMEROFILE"
    GRUNNLAG_MODEL = "GRUNNLAG_MODEL"
    GRUNNLAG_SAMPLE = "GRUNNLAG_SAMPLE"
    GRUNNLAG_STAGE = "GRUNNLAG_STAGE"
    GRUNNLAG_CHANNEL = "GRUNNLAG_CHANNEL"
    GRUNNLAG_POSITION = "GRUNNLAG_POSITION"
    GRUNNLAG_ERA = "GRUNNLAG_ERA"
    GRUNNLAG_TIMEPOINT = "GRUNNLAG_TIMEPOINT"
    GRUNNLAG_REPRESENTATION = "GRUNNLAG_REPRESENTATION"
    GRUNNLAG_OMERO = "GRUNNLAG_OMERO"
    GRUNNLAG_DIMENSIONMAP = "GRUNNLAG_DIMENSIONMAP"
    GRUNNLAG_VIEW = "GRUNNLAG_VIEW"
    GRUNNLAG_METRIC = "GRUNNLAG_METRIC"
    GRUNNLAG_THUMBNAIL = "GRUNNLAG_THUMBNAIL"
    GRUNNLAG_VIDEO = "GRUNNLAG_VIDEO"
    GRUNNLAG_ROI = "GRUNNLAG_ROI"
    GRUNNLAG_LABEL = "GRUNNLAG_LABEL"
    GRUNNLAG_FEATURE = "GRUNNLAG_FEATURE"
    BORD_TABLE = "BORD_TABLE"
    BORD_GRAPH = "BORD_GRAPH"
    PLOTQL_PLOT = "PLOTQL_PLOT"


class OmeroFileType(str, Enum):
    """An enumeration."""

    TIFF = "TIFF"
    "Tiff"
    JPEG = "JPEG"
    "Jpeg"
    MSR = "MSR"
    "MSR File"
    CZI = "CZI"
    "Zeiss Microscopy File"
    UNKNOWN = "UNKNOWN"
    "Unwknon File Format"


class RepresentationVarietyInput(str, Enum):
    """Variety expresses the Type of Representation we are dealing with"""

    MASK = "MASK"
    "Mask (Value represent Labels)"
    VOXEL = "VOXEL"
    "Voxel (Value represent Intensity)"
    RGB = "RGB"
    "RGB (First three channel represent RGB)"
    UNKNOWN = "UNKNOWN"
    "Unknown"


class PandasDType(str, Enum):
    OBJECT = "OBJECT"
    INT64 = "INT64"
    FLOAT64 = "FLOAT64"
    BOOL = "BOOL"
    CATEGORY = "CATEGORY"
    DATETIME65 = "DATETIME65"
    TIMEDELTA = "TIMEDELTA"
    UNICODE = "UNICODE"
    DATETIME = "DATETIME"
    DATETIMEZ = "DATETIMEZ"
    DATETIMETZ = "DATETIMETZ"
    DATETIME64 = "DATETIME64"
    DATETIME64TZ = "DATETIME64TZ"
    DATETIME64NS = "DATETIME64NS"
    DATETIME64NSUTC = "DATETIME64NSUTC"
    DATETIME64NSZ = "DATETIME64NSZ"
    DATETIME64NSZUTC = "DATETIME64NSZUTC"


class ROIType(str, Enum):
    """An enumeration."""

    ELLIPSE = "ELLIPSE"
    "Ellipse"
    POLYGON = "POLYGON"
    "POLYGON"
    LINE = "LINE"
    "Line"
    RECTANGLE = "RECTANGLE"
    "Rectangle"
    PATH = "PATH"
    "Path"
    UNKNOWN = "UNKNOWN"
    "Unknown"
    FRAME = "FRAME"
    "Frame"
    SLICE = "SLICE"
    "Slice"
    POINT = "POINT"
    "Point"


class Dimension(str, Enum):
    """The dimension of the data"""

    X = "X"
    Y = "Y"
    Z = "Z"
    T = "T"
    C = "C"


class Medium(str, Enum):
    """The medium of the imaging environment

    Important for the objective settings"""

    AIR = "AIR"
    GLYCEROL = "GLYCEROL"
    OIL = "OIL"
    OTHER = "OTHER"
    WATER = "WATER"


class RoiTypeInput(str, Enum):
    """An enumeration."""

    ELLIPSIS = "ELLIPSIS"
    "Ellipse"
    POLYGON = "POLYGON"
    "POLYGON"
    LINE = "LINE"
    "Line"
    RECTANGLE = "RECTANGLE"
    "Rectangle"
    PATH = "PATH"
    "Path"
    UNKNOWN = "UNKNOWN"
    "Unknown"
    FRAME = "FRAME"
    "Frame"
    SLICE = "SLICE"
    "Slice"
    POINT = "POINT"
    "Point"


class RepresentationVariety(str, Enum):
    """An enumeration."""

    MASK = "MASK"
    "Mask (Value represent Labels)"
    VOXEL = "VOXEL"
    "Voxel (Value represent Intensity)"
    RGB = "RGB"
    "RGB (First three channel represent RGB)"
    UNKNOWN = "UNKNOWN"
    "Unknown"


class ModelKind(str, Enum):
    """What format is the model in?"""

    ONNX = "ONNX"
    TENSORFLOW = "TENSORFLOW"
    PYTORCH = "PYTORCH"
    UNKNOWN = "UNKNOWN"


class AcquisitionKind(str, Enum):
    """What do the multiple positions in this acquistion represent?"""

    POSTION_IS_SAMPLE = "POSTION_IS_SAMPLE"
    POSITION_IS_ROI = "POSITION_IS_ROI"
    UNKNOWN = "UNKNOWN"


class DescendendInput(BaseModel):
    children: Optional[Tuple[Optional["DescendendInput"], ...]]
    typename: Optional[str]
    "The type of the descendent"
    user: Optional[str]
    "The user that is mentioned"
    bold: Optional[bool]
    "Is this a bold leaf?"
    italic: Optional[bool]
    "Is this a italic leaf?"
    code: Optional[bool]
    "Is this a code leaf?"
    text: Optional[str]
    "The text of the leaf"

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class GroupAssignmentInput(BaseModel):
    permissions: Tuple[Optional[str], ...]
    group: ID

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class UserAssignmentInput(BaseModel):
    permissions: Tuple[Optional[str], ...]
    user: str
    "The user id"

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class OmeroRepresentationInput(BaseModel):
    """The Omero Meta Data of an Image

    Follows closely the omexml model. With a few alterations:
    - The data model of the datasets and experimenters is
    part of the mikro datamodel and are not accessed here.
    - Some parameters are ommited as they are not really used"""

    planes: Optional[Tuple[Optional["PlaneInput"], ...]]
    maps: Optional[Tuple[Optional[ID], ...]]
    timepoints: Optional[Tuple[Optional[ID], ...]]
    channels: Optional[Tuple[Optional["ChannelInput"], ...]]
    physical_size: Optional["PhysicalSizeInput"] = Field(alias="physicalSize")
    affine_transformation: Optional[AffineMatrix] = Field(alias="affineTransformation")
    scale: Optional[Tuple[Optional[float], ...]]
    positions: Optional[Tuple[Optional[ID], ...]]
    cameras: Optional[Tuple[Optional[ID], ...]]
    acquisition_date: Optional[datetime] = Field(alias="acquisitionDate")
    objective_settings: Optional["ObjectiveSettingsInput"] = Field(
        alias="objectiveSettings"
    )
    imaging_environment: Optional["ImagingEnvironmentInput"] = Field(
        alias="imagingEnvironment"
    )
    instrument: Optional[ID]
    objective: Optional[ID]

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class PlaneInput(BaseModel):
    """ " A plane in an image

    Plane follows the convention of the OME model, where the first index is the
    Z axis, the second is the Y axis, the third is the X axis, the fourth is the
    C axis, and the fifth is the T axis.

    It attached the image at the indicated index to the image and gives information
    about the plane (e.g. exposure time, delta t to the origin, etc.)"""

    z: Optional[int]
    "Z index of the plane"
    y: Optional[int]
    "Y index of the plane"
    x: Optional[int]
    "X index of the plane"
    c: Optional[int]
    "C index of the plane"
    t: Optional[int]
    "Z index of the plane"
    position_x: Optional[float] = Field(alias="positionX")
    "The planes X position on the stage of the microscope"
    position_y: Optional[float] = Field(alias="positionY")
    "The planes Y position on the stage of the microscope"
    position_z: Optional[float] = Field(alias="positionZ")
    "The planes Z position on the stage of the microscope"
    exposure_time: Optional[float] = Field(alias="exposureTime")
    "The exposure time of the plane (e.g. Laser exposure)"
    delta_t: Optional[float] = Field(alias="deltaT")
    "The Delta T to the origin of the image acqusition"

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class ChannelInput(BaseModel):
    """A channel in an image

    Channels can be highly variable in their properties. This class is a
    representation of the most common properties of a channel."""

    name: Optional[str]
    "The name of the channel"
    emmission_wavelength: Optional[float] = Field(alias="emmissionWavelength")
    "The emmission wavelength of the fluorophore in nm"
    excitation_wavelength: Optional[float] = Field(alias="excitationWavelength")
    "The excitation wavelength of the fluorophore in nm"
    acquisition_mode: Optional[str] = Field(alias="acquisitionMode")
    "The acquisition mode of the channel"
    color: Optional[str]
    "The default color for the channel (might be ommited by the rendered)"

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class PhysicalSizeInput(BaseModel):
    """Physical size of the image

    Each dimensions of the image has a physical size. This is the size of the
    pixel in the image. The physical size is given in micrometers on a PIXEL
    basis. This means that the physical size of the image is the size of the
    pixel in the image * the number of pixels in the image. For example, if
    the image is 1000x1000 pixels and the physical size of the image is 3 (x params) x 3 (y params),
    micrometer, the physical size of the image is 3000x3000 micrometer. If the image

    The t dimension is given in ms, since the time is given in ms.
    The C dimension is given in nm, since the wavelength is given in nm."""

    x: Optional[float]
    "Physical size of *one* Pixel in the x dimension (in µm)"
    y: Optional[float]
    "Physical size of *one* Pixel in the t dimension (in µm)"
    z: Optional[float]
    "Physical size of *one* Pixel in the z dimension (in µm)"
    t: Optional[float]
    "Physical size of *one* Pixel in the t dimension (in ms)"
    c: Optional[float]
    "Physical size of *one* Pixel in the c dimension (in nm)"

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class ObjectiveSettingsInput(BaseModel):
    """Settings of the objective used to acquire the image

    Follows the OME model for objective settings"""

    correction_collar: Optional[float] = Field(alias="correctionCollar")
    "The correction collar of the objective"
    medium: Optional[Medium]
    "The medium of the objective"
    numerical_aperture: Optional[float] = Field(alias="numericalAperture")
    "The numerical aperture of the objective"
    working_distance: Optional[float] = Field(alias="workingDistance")
    "The working distance of the objective"

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class ImagingEnvironmentInput(BaseModel):
    """The imaging environment during the acquisition

    Follows the OME model for imaging environment"""

    air_pressure: Optional[float] = Field(alias="airPressure")
    "The air pressure during the acquisition"
    co2_percent: Optional[float] = Field(alias="co2Percent")
    "The CO2 percentage in the environment"
    humidity: Optional[float]
    "The humidity of the imaging environment"
    temperature: Optional[float]
    "The temperature of the imaging environment"
    map: Optional[Dict]
    "A map of the imaging environment. Key value based"

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class RepresentationViewInput(BaseModel):
    z_min: Optional[int] = Field(alias="zMin")
    "The x coord of the position (relative to origin)"
    z_max: Optional[int] = Field(alias="zMax")
    "The x coord of the position (relative to origin)"
    t_min: Optional[int] = Field(alias="tMin")
    "The x coord of the position (relative to origin)"
    t_max: Optional[int] = Field(alias="tMax")
    "The x coord of the position (relative to origin)"
    c_min: Optional[int] = Field(alias="cMin")
    "The x coord of the position (relative to origin)"
    c_max: Optional[int] = Field(alias="cMax")
    "The x coord of the position (relative to origin)"
    x_min: Optional[int] = Field(alias="xMin")
    "The x coord of the position (relative to origin)"
    x_max: Optional[int] = Field(alias="xMax")
    "The x coord of the position (relative to origin)"
    y_min: Optional[int] = Field(alias="yMin")
    "The x coord of the position (relative to origin)"
    y_max: Optional[int] = Field(alias="yMax")
    "The x coord of the position (relative to origin)"
    channel: Optional[ID]
    "The channel you want to associate with this map"
    position: Optional[ID]
    "The position you want to associate with this map"
    timepoint: Optional[ID]
    "The position you want to associate with this map"
    created_while: Optional[AssignationID] = Field(alias="createdWhile")
    "The assignation id"

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class InputVector(Vectorizable, BaseModel):
    x: Optional[float]
    "X-coordinate"
    y: Optional[float]
    "Y-coordinate"
    z: Optional[float]
    "Z-coordinate"
    c: Optional[float]
    "C-coordinate"
    t: Optional[float]
    "T-coordinate"

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class ViewInput(BaseModel):
    omero: ID
    "The stage this position belongs to"
    z_min: Optional[int] = Field(alias="zMin")
    "The x coord of the position (relative to origin)"
    z_max: Optional[int] = Field(alias="zMax")
    "The x coord of the position (relative to origin)"
    t_min: Optional[int] = Field(alias="tMin")
    "The x coord of the position (relative to origin)"
    t_max: Optional[int] = Field(alias="tMax")
    "The x coord of the position (relative to origin)"
    c_min: Optional[int] = Field(alias="cMin")
    "The x coord of the position (relative to origin)"
    c_max: Optional[int] = Field(alias="cMax")
    "The x coord of the position (relative to origin)"
    x_min: Optional[int] = Field(alias="xMin")
    "The x coord of the position (relative to origin)"
    x_max: Optional[int] = Field(alias="xMax")
    "The x coord of the position (relative to origin)"
    y_min: Optional[int] = Field(alias="yMin")
    "The x coord of the position (relative to origin)"
    y_max: Optional[int] = Field(alias="yMax")
    "The x coord of the position (relative to origin)"
    channel: Optional[ID]
    "The channel you want to associate with this map"
    position: Optional[ID]
    "The position you want to associate with this map"
    timepoint: Optional[ID]
    "The position you want to associate with this map"
    created_while: Optional[AssignationID] = Field(alias="createdWhile")
    "The assignation id"

    class Config:
        frozen = True
        extra = "forbid"
        use_enum_values = True


class DetailLabelFragmentFeatures(BaseModel):
    """A Feature is a numerical key value pair that is attached to a Label.

    You can model it for example as a key value pair of a class instance of a segmentation mask.
    Representation -> Label0 -> Feature0
                             -> Feature1
                   -> Label1 -> Feature0

    Features can be used to store any numerical value that is attached to a class instance.
    THere can only ever be one key per label. If you want to store multiple values for a key, you can
    store them as a list in the value field.

    Feature are analogous to metrics on a representation, but for a specific class instance (Label)

    """

    typename: Optional[Literal["Feature"]] = Field(alias="__typename", exclude=True)
    id: ID
    key: str
    "The key of the feature"
    value: Optional[FeatureValue]
    "Value"

    class Config:
        frozen = True


class DetailLabelFragment(BaseModel):
    typename: Optional[Literal["Label"]] = Field(alias="__typename", exclude=True)
    id: ID
    instance: int
    "The instance value of the representation (pixel value). Must be a value of the image array"
    name: Optional[str]
    "The name of the instance"
    features: Optional[Tuple[Optional[DetailLabelFragmentFeatures], ...]]
    "Features attached to this Label"

    class Config:
        frozen = True


class MultiScaleSampleFragmentRepresentationsDerived(Representation, BaseModel):
    """A Representation is 5-dimensional representation of an image

    Mikro stores each image as sa 5-dimensional representation. The dimensions are:
    - t: time
    - c: channel
    - z: z-stack
    - x: x-dimension
    - y: y-dimension

    This ensures a unified api for all images, regardless of their original dimensions. Another main
    determining factor for a representation is its variety:
    A representation can be a raw image representating voxels (VOXEL)
    or a segmentation mask representing instances of a class. (MASK)
    It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

    # Meta

    Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


    #Origins and Derivations

    Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
    Both are encapsulaed in the origins and derived fields.

    Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
    Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
    File and Rois that are used to create images are saved in the file origins and roi origins repectively.


    """

    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    store: Optional[Store]

    class Config:
        frozen = True


class MultiScaleSampleFragmentRepresentations(Representation, BaseModel):
    """A Representation is 5-dimensional representation of an image

    Mikro stores each image as sa 5-dimensional representation. The dimensions are:
    - t: time
    - c: channel
    - z: z-stack
    - x: x-dimension
    - y: y-dimension

    This ensures a unified api for all images, regardless of their original dimensions. Another main
    determining factor for a representation is its variety:
    A representation can be a raw image representating voxels (VOXEL)
    or a segmentation mask representing instances of a class. (MASK)
    It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

    # Meta

    Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


    #Origins and Derivations

    Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
    Both are encapsulaed in the origins and derived fields.

    Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
    Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
    File and Rois that are used to create images are saved in the file origins and roi origins repectively.


    """

    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    store: Optional[Store]
    derived: Optional[
        Tuple[Optional[MultiScaleSampleFragmentRepresentationsDerived], ...]
    ]
    "Derived Images from this Image"

    class Config:
        frozen = True


class MultiScaleSampleFragment(BaseModel):
    typename: Optional[Literal["Sample"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    "The name of the sample"
    representations: Optional[
        Tuple[Optional[MultiScaleSampleFragmentRepresentations], ...]
    ]
    "Associated representations of this Sample"

    class Config:
        frozen = True


class ROIFragmentVectors(BaseModel):
    typename: Optional[Literal["Vector"]] = Field(alias="__typename", exclude=True)
    x: Optional[float]
    "X-coordinate"
    y: Optional[float]
    "Y-coordinate"
    z: Optional[float]
    "Z-coordinate"
    t: Optional[float]
    "T-coordinate"
    c: Optional[float]
    "C-coordinate"

    class Config:
        frozen = True


class ROIFragmentRepresentation(Representation, BaseModel):
    """A Representation is 5-dimensional representation of an image

    Mikro stores each image as sa 5-dimensional representation. The dimensions are:
    - t: time
    - c: channel
    - z: z-stack
    - x: x-dimension
    - y: y-dimension

    This ensures a unified api for all images, regardless of their original dimensions. Another main
    determining factor for a representation is its variety:
    A representation can be a raw image representating voxels (VOXEL)
    or a segmentation mask representing instances of a class. (MASK)
    It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

    # Meta

    Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


    #Origins and Derivations

    Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
    Both are encapsulaed in the origins and derived fields.

    Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
    Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
    File and Rois that are used to create images are saved in the file origins and roi origins repectively.


    """

    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID

    class Config:
        frozen = True


class ROIFragmentCreator(BaseModel):
    """User

    This object represents a user in the system. Users are used to
    control access to different parts of the system. Users are assigned
    to groups. A user has access to a part of the system if the user is
    a member of a group that has the permission assigned to it.

    Users can be be "creator" of objects. This means that the user has
    created the object. This is used to control access to objects. A user
    can only access objects that they have created, or objects that they
    have access to through a group that they are a member of.

    See the documentation for "Object Level Permissions" for more information."""

    typename: Optional[Literal["User"]] = Field(alias="__typename", exclude=True)
    id: ID
    color: str
    "The prefered color of the user"

    class Config:
        frozen = True


class ROIFragment(ROI, BaseModel):
    typename: Optional[Literal["ROI"]] = Field(alias="__typename", exclude=True)
    id: ID
    vectors: Optional[Tuple[Optional[ROIFragmentVectors], ...]]
    "The vectors of the ROI"
    type: ROIType
    "The Roi can have varying types, consult your API"
    representation: Optional[ROIFragmentRepresentation]
    "The Representation this ROI was original used to create (drawn on)"
    creator: ROIFragmentCreator
    "The user that created the ROI"

    class Config:
        frozen = True


class MultiScaleRepresentationFragmentDerived(Representation, BaseModel):
    """A Representation is 5-dimensional representation of an image

    Mikro stores each image as sa 5-dimensional representation. The dimensions are:
    - t: time
    - c: channel
    - z: z-stack
    - x: x-dimension
    - y: y-dimension

    This ensures a unified api for all images, regardless of their original dimensions. Another main
    determining factor for a representation is its variety:
    A representation can be a raw image representating voxels (VOXEL)
    or a segmentation mask representing instances of a class. (MASK)
    It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

    # Meta

    Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


    #Origins and Derivations

    Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
    Both are encapsulaed in the origins and derived fields.

    Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
    Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
    File and Rois that are used to create images are saved in the file origins and roi origins repectively.


    """

    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    name: Optional[str]
    "Cleartext name"
    tags: Optional[Tuple[Optional[str], ...]]
    "A comma-separated list of tags."
    meta: Optional[Dict]
    store: Optional[Store]

    class Config:
        frozen = True


class MultiScaleRepresentationFragment(Representation, BaseModel):
    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    derived: Optional[Tuple[Optional[MultiScaleRepresentationFragmentDerived], ...]]
    "Derived Images from this Image"

    class Config:
        frozen = True


class RepresentationFragmentSample(BaseModel):
    """Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure), was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample"""

    typename: Optional[Literal["Sample"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    "The name of the sample"

    class Config:
        frozen = True


class RepresentationFragmentOmero(Omero, BaseModel):
    """Omero is a through model that stores the real world context of an image

    This means that it stores the position (corresponding to the relative displacement to
    a stage (Both are models)), objective and other meta data of the image.

    """

    typename: Optional[Literal["Omero"]] = Field(alias="__typename", exclude=True)
    scale: Optional[Tuple[Optional[float], ...]]

    class Config:
        frozen = True


class RepresentationFragment(Representation, BaseModel):
    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    sample: Optional[RepresentationFragmentSample]
    "The Sample this representation belosngs to"
    id: ID
    store: Optional[Store]
    variety: RepresentationVariety
    "The Representation can have vasrying types, consult your API"
    name: Optional[str]
    "Cleartext name"
    omero: Optional[RepresentationFragmentOmero]

    class Config:
        frozen = True


class DetailRepresentationFragmentSample(BaseModel):
    """Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure), was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample"""

    typename: Optional[Literal["Sample"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    "The name of the sample"

    class Config:
        frozen = True


class DetailRepresentationFragmentOmeroPhysicalsize(PhysicalSize, BaseModel):
    """Physical size of the image

    Each dimensions of the image has a physical size. This is the size of the
    pixel in the image. The physical size is given in micrometers on a PIXEL
    basis. This means that the physical size of the image is the size of the
    pixel in the image * the number of pixels in the image. For example, if
    the image is 1000x1000 pixels and the physical size of the image is 3 (x params) x 3 (y params),
    micrometer, the physical size of the image is 3000x3000 micrometer. If the image

    The t dimension is given in ms, since the time is given in ms.
    The C dimension is given in nm, since the wavelength is given in nm."""

    typename: Optional[Literal["PhysicalSize"]] = Field(
        alias="__typename", exclude=True
    )
    x: Optional[float]
    "Physical size of *one* Pixel in the x dimension (in µm)"
    y: Optional[float]
    "Physical size of *one* Pixel in the t dimension (in µm)"
    z: Optional[float]
    "Physical size of *one* Pixel in the z dimension (in µm)"

    class Config:
        frozen = True


class DetailRepresentationFragmentOmeroPositionsStage(Stage, BaseModel):
    """An Stage is a set of positions that share a common space on a microscope and can
    be use to translate.


    """

    typename: Optional[Literal["Stage"]] = Field(alias="__typename", exclude=True)
    name: str
    "The name of the stage"
    id: ID

    class Config:
        frozen = True


class DetailRepresentationFragmentOmeroPositions(Position, BaseModel):
    """The relative position of a sample on a microscope stage"""

    typename: Optional[Literal["Position"]] = Field(alias="__typename", exclude=True)
    name: str
    "The name of the possition"
    id: ID
    x: float
    "pixelSize for x in microns"
    y: float
    "pixelSize for y in microns"
    z: float
    "pixelSize for z in microns"
    stage: DetailRepresentationFragmentOmeroPositionsStage

    class Config:
        frozen = True


class DetailRepresentationFragmentOmeroTimepointsEra(BaseModel):
    """Era(id, created_by, created_through, created_while, name, start, end, created_at)"""

    typename: Optional[Literal["Era"]] = Field(alias="__typename", exclude=True)
    name: str
    "The name of the era"
    id: ID

    class Config:
        frozen = True


class DetailRepresentationFragmentOmeroTimepoints(BaseModel):
    """The relative position of a sample on a microscope stage"""

    typename: Optional[Literal["Timepoint"]] = Field(alias="__typename", exclude=True)
    name: Optional[str]
    "The name of the timepoint"
    id: ID
    era: DetailRepresentationFragmentOmeroTimepointsEra

    class Config:
        frozen = True


class DetailRepresentationFragmentOmeroViewsChannel(BaseModel):
    """Channel(id, created_by, created_through, created_while, name, emission_wavelength, excitation_wavelength, acquisition_mode, color)"""

    typename: Optional[Literal["Channel"]] = Field(alias="__typename", exclude=True)
    name: str
    "The name of the channel"
    id: ID

    class Config:
        frozen = True


class DetailRepresentationFragmentOmeroViewsPosition(Position, BaseModel):
    """The relative position of a sample on a microscope stage"""

    typename: Optional[Literal["Position"]] = Field(alias="__typename", exclude=True)
    name: str
    "The name of the possition"
    id: ID
    x: float
    "pixelSize for x in microns"
    y: float
    "pixelSize for y in microns"
    z: float
    "pixelSize for z in microns"

    class Config:
        frozen = True


class DetailRepresentationFragmentOmeroViewsTimepoint(BaseModel):
    """The relative position of a sample on a microscope stage"""

    typename: Optional[Literal["Timepoint"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        frozen = True


class DetailRepresentationFragmentOmeroViews(BaseModel):
    """View(id, created_by, created_through, created_while, omero, z_min, z_max, x_min, x_max, y_min, y_max, t_min, t_max, c_min, c_max, channel, position, objective, instrument, timepoint)"""

    typename: Optional[Literal["View"]] = Field(alias="__typename", exclude=True)
    channel: Optional[DetailRepresentationFragmentOmeroViewsChannel]
    position: Optional[DetailRepresentationFragmentOmeroViewsPosition]
    timepoint: Optional[DetailRepresentationFragmentOmeroViewsTimepoint]

    class Config:
        frozen = True


class DetailRepresentationFragmentOmero(Omero, BaseModel):
    """Omero is a through model that stores the real world context of an image

    This means that it stores the position (corresponding to the relative displacement to
    a stage (Both are models)), objective and other meta data of the image.

    """

    typename: Optional[Literal["Omero"]] = Field(alias="__typename", exclude=True)
    physical_size: Optional[DetailRepresentationFragmentOmeroPhysicalsize] = Field(
        alias="physicalSize"
    )
    positions: Tuple[DetailRepresentationFragmentOmeroPositions, ...]
    timepoints: Optional[
        Tuple[Optional[DetailRepresentationFragmentOmeroTimepoints], ...]
    ]
    "Associated Timepoints"
    views: Optional[Tuple[Optional[DetailRepresentationFragmentOmeroViews], ...]]
    "Associated views"

    class Config:
        frozen = True


class DetailRepresentationFragmentMetricsRepresentation(Representation, BaseModel):
    """A Representation is 5-dimensional representation of an image

    Mikro stores each image as sa 5-dimensional representation. The dimensions are:
    - t: time
    - c: channel
    - z: z-stack
    - x: x-dimension
    - y: y-dimension

    This ensures a unified api for all images, regardless of their original dimensions. Another main
    determining factor for a representation is its variety:
    A representation can be a raw image representating voxels (VOXEL)
    or a segmentation mask representing instances of a class. (MASK)
    It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

    # Meta

    Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


    #Origins and Derivations

    Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
    Both are encapsulaed in the origins and derived fields.

    Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
    Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
    File and Rois that are used to create images are saved in the file origins and roi origins repectively.


    """

    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID

    class Config:
        frozen = True


class DetailRepresentationFragmentMetrics(BaseModel):
    typename: Optional[Literal["Metric"]] = Field(alias="__typename", exclude=True)
    id: ID
    key: str
    "The Key"
    value: Optional[MetricValue]
    "Value"
    representation: Optional[DetailRepresentationFragmentMetricsRepresentation]
    "The Representatoin this Metric belongs to"

    class Config:
        frozen = True


class DetailRepresentationFragmentDerived(Representation, BaseModel):
    """A Representation is 5-dimensional representation of an image

    Mikro stores each image as sa 5-dimensional representation. The dimensions are:
    - t: time
    - c: channel
    - z: z-stack
    - x: x-dimension
    - y: y-dimension

    This ensures a unified api for all images, regardless of their original dimensions. Another main
    determining factor for a representation is its variety:
    A representation can be a raw image representating voxels (VOXEL)
    or a segmentation mask representing instances of a class. (MASK)
    It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

    # Meta

    Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


    #Origins and Derivations

    Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
    Both are encapsulaed in the origins and derived fields.

    Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
    Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
    File and Rois that are used to create images are saved in the file origins and roi origins repectively.


    """

    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    name: Optional[str]
    "Cleartext name"
    store: Optional[Store]

    class Config:
        frozen = True


class DetailRepresentationFragment(Representation, BaseModel):
    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    sample: Optional[DetailRepresentationFragmentSample]
    "The Sample this representation belosngs to"
    id: ID
    store: Optional[Store]
    shape: Optional[Tuple[int, ...]]
    "The arrays shape format [c,t,z,y,x]"
    variety: RepresentationVariety
    "The Representation can have vasrying types, consult your API"
    name: Optional[str]
    "Cleartext name"
    omero: Optional[DetailRepresentationFragmentOmero]
    metrics: Optional[Tuple[Optional[DetailRepresentationFragmentMetrics], ...]]
    "Associated metrics of this Imasge"
    derived: Optional[Tuple[Optional[DetailRepresentationFragmentDerived], ...]]
    "Derived Images from this Image"

    class Config:
        frozen = True


class RepresentationAndMaskFragmentSample(BaseModel):
    """Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure), was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample"""

    typename: Optional[Literal["Sample"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    "The name of the sample"

    class Config:
        frozen = True


class RepresentationAndMaskFragmentDerived(Representation, BaseModel):
    """A Representation is 5-dimensional representation of an image

    Mikro stores each image as sa 5-dimensional representation. The dimensions are:
    - t: time
    - c: channel
    - z: z-stack
    - x: x-dimension
    - y: y-dimension

    This ensures a unified api for all images, regardless of their original dimensions. Another main
    determining factor for a representation is its variety:
    A representation can be a raw image representating voxels (VOXEL)
    or a segmentation mask representing instances of a class. (MASK)
    It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

    # Meta

    Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


    #Origins and Derivations

    Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
    Both are encapsulaed in the origins and derived fields.

    Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
    Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
    File and Rois that are used to create images are saved in the file origins and roi origins repectively.


    """

    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    store: Optional[Store]
    variety: RepresentationVariety
    "The Representation can have vasrying types, consult your API"
    name: Optional[str]
    "Cleartext name"

    class Config:
        frozen = True


class RepresentationAndMaskFragmentOmero(Omero, BaseModel):
    """Omero is a through model that stores the real world context of an image

    This means that it stores the position (corresponding to the relative displacement to
    a stage (Both are models)), objective and other meta data of the image.

    """

    typename: Optional[Literal["Omero"]] = Field(alias="__typename", exclude=True)
    scale: Optional[Tuple[Optional[float], ...]]

    class Config:
        frozen = True


class RepresentationAndMaskFragment(Representation, BaseModel):
    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    sample: Optional[RepresentationAndMaskFragmentSample]
    "The Sample this representation belosngs to"
    id: ID
    store: Optional[Store]
    variety: RepresentationVariety
    "The Representation can have vasrying types, consult your API"
    name: Optional[str]
    "Cleartext name"
    derived: Optional[Tuple[Optional[RepresentationAndMaskFragmentDerived], ...]]
    "Derived Images from this Image"
    omero: Optional[RepresentationAndMaskFragmentOmero]

    class Config:
        frozen = True


class ListRepresentationFragmentSample(BaseModel):
    """Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure), was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample"""

    typename: Optional[Literal["Sample"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    "The name of the sample"

    class Config:
        frozen = True


class ListRepresentationFragment(Representation, BaseModel):
    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    name: Optional[str]
    "Cleartext name"
    sample: Optional[ListRepresentationFragmentSample]
    "The Sample this representation belosngs to"

    class Config:
        frozen = True


class Watch_roisSubscriptionRois(BaseModel):
    typename: Optional[Literal["RoiEvent"]] = Field(alias="__typename", exclude=True)
    update: Optional[ROIFragment]
    delete: Optional[ID]
    create: Optional[ROIFragment]

    class Config:
        frozen = True


class Watch_roisSubscription(BaseModel):
    rois: Optional[Watch_roisSubscriptionRois]

    class Arguments(BaseModel):
        representation: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  vectors {\n    x\n    y\n    z\n    t\n    c\n  }\n  type\n  representation {\n    id\n  }\n  creator {\n    id\n    color\n  }\n}\n\nsubscription watch_rois($representation: ID!) {\n  rois(representation: $representation) {\n    update {\n      ...ROI\n    }\n    delete\n    create {\n      ...ROI\n    }\n  }\n}"


class Create_roiMutation(BaseModel):
    create_roi: Optional[ROIFragment] = Field(alias="createROI")
    "Creates a Sample"

    class Arguments(BaseModel):
        representation: ID
        vectors: List[Optional[InputVector]]
        creator: Optional[ID] = Field(default=None)
        type: RoiTypeInput

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  vectors {\n    x\n    y\n    z\n    t\n    c\n  }\n  type\n  representation {\n    id\n  }\n  creator {\n    id\n    color\n  }\n}\n\nmutation create_roi($representation: ID!, $vectors: [InputVector]!, $creator: ID, $type: RoiTypeInput!) {\n  createROI(\n    representation: $representation\n    vectors: $vectors\n    type: $type\n    creator: $creator\n  ) {\n    ...ROI\n  }\n}"


class Delete_roiMutationDeleteroi(BaseModel):
    typename: Optional[Literal["DeleteROIResult"]] = Field(
        alias="__typename", exclude=True
    )
    id: Optional[str]

    class Config:
        frozen = True


class Delete_roiMutation(BaseModel):
    delete_roi: Optional[Delete_roiMutationDeleteroi] = Field(alias="deleteROI")
    "Create an experiment (only signed in users)"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = (
            "mutation delete_roi($id: ID!) {\n  deleteROI(id: $id) {\n    id\n  }\n}"
        )


class Get_label_forQuery(BaseModel):
    label_for: Optional[DetailLabelFragment] = Field(alias="labelFor")
    "Get a label for a specific instance on a specific representation\n    \n    "

    class Arguments(BaseModel):
        representation: ID
        instance: int

    class Meta:
        document = "fragment DetailLabel on Label {\n  id\n  instance\n  name\n  features {\n    id\n    key\n    value\n  }\n}\n\nquery get_label_for($representation: ID!, $instance: Int!) {\n  labelFor(representation: $representation, instance: $instance) {\n    ...DetailLabel\n  }\n}"


class Get_image_stageQueryStagePositionsOmerosRepresentation(Representation, BaseModel):
    """A Representation is 5-dimensional representation of an image

    Mikro stores each image as sa 5-dimensional representation. The dimensions are:
    - t: time
    - c: channel
    - z: z-stack
    - x: x-dimension
    - y: y-dimension

    This ensures a unified api for all images, regardless of their original dimensions. Another main
    determining factor for a representation is its variety:
    A representation can be a raw image representating voxels (VOXEL)
    or a segmentation mask representing instances of a class. (MASK)
    It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

    # Meta

    Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


    #Origins and Derivations

    Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
    Both are encapsulaed in the origins and derived fields.

    Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
    Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
    File and Rois that are used to create images are saved in the file origins and roi origins repectively.


    """

    typename: Optional[Literal["Representation"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    shape: Optional[Tuple[int, ...]]
    "The arrays shape format [c,t,z,y,x]"
    store: Optional[Store]

    class Config:
        frozen = True


class Get_image_stageQueryStagePositionsOmerosPhysicalsize(PhysicalSize, BaseModel):
    """Physical size of the image

    Each dimensions of the image has a physical size. This is the size of the
    pixel in the image. The physical size is given in micrometers on a PIXEL
    basis. This means that the physical size of the image is the size of the
    pixel in the image * the number of pixels in the image. For example, if
    the image is 1000x1000 pixels and the physical size of the image is 3 (x params) x 3 (y params),
    micrometer, the physical size of the image is 3000x3000 micrometer. If the image

    The t dimension is given in ms, since the time is given in ms.
    The C dimension is given in nm, since the wavelength is given in nm."""

    typename: Optional[Literal["PhysicalSize"]] = Field(
        alias="__typename", exclude=True
    )
    x: Optional[float]
    "Physical size of *one* Pixel in the x dimension (in µm)"
    y: Optional[float]
    "Physical size of *one* Pixel in the t dimension (in µm)"
    z: Optional[float]
    "Physical size of *one* Pixel in the z dimension (in µm)"
    t: Optional[float]
    "Physical size of *one* Pixel in the t dimension (in ms)"
    c: Optional[float]
    "Physical size of *one* Pixel in the c dimension (in µm)"

    class Config:
        frozen = True


class Get_image_stageQueryStagePositionsOmeros(Omero, BaseModel):
    """Omero is a through model that stores the real world context of an image

    This means that it stores the position (corresponding to the relative displacement to
    a stage (Both are models)), objective and other meta data of the image.

    """

    typename: Optional[Literal["Omero"]] = Field(alias="__typename", exclude=True)
    id: ID
    acquisition_date: Optional[datetime] = Field(alias="acquisitionDate")
    representation: Get_image_stageQueryStagePositionsOmerosRepresentation
    physical_size: Optional[
        Get_image_stageQueryStagePositionsOmerosPhysicalsize
    ] = Field(alias="physicalSize")

    class Config:
        frozen = True


class Get_image_stageQueryStagePositions(Position, BaseModel):
    """The relative position of a sample on a microscope stage"""

    typename: Optional[Literal["Position"]] = Field(alias="__typename", exclude=True)
    x: float
    "pixelSize for x in microns"
    y: float
    "pixelSize for y in microns"
    z: float
    "pixelSize for z in microns"
    omeros: Optional[Tuple[Optional[Get_image_stageQueryStagePositionsOmeros], ...]]
    "Associated images through Omero"

    class Config:
        frozen = True


class Get_image_stageQueryStage(Stage, BaseModel):
    """An Stage is a set of positions that share a common space on a microscope and can
    be use to translate.


    """

    typename: Optional[Literal["Stage"]] = Field(alias="__typename", exclude=True)
    positions: Tuple[Get_image_stageQueryStagePositions, ...]

    class Config:
        frozen = True


class Get_image_stageQuery(BaseModel):
    stage: Optional[Get_image_stageQueryStage]
    'Get a single experiment by ID"\n    \n    Returns a single experiment by ID. If the user does not have access\n    to the experiment, an error will be raised.\n    \n    '

    class Arguments(BaseModel):
        id: ID
        limit: Optional[int] = Field(default=None)

    class Meta:
        document = 'query get_image_stage($id: ID!, $limit: Int) {\n  stage(id: $id) {\n    positions {\n      x\n      y\n      z\n      omeros(order: "-acquired", limit: $limit) {\n        id\n        acquisitionDate\n        representation {\n          id\n          shape\n          store\n        }\n        physicalSize {\n          x\n          y\n          z\n          t\n          c\n        }\n      }\n    }\n  }\n}'


class Expand_multiscaleQuery(BaseModel):
    sample: Optional[MultiScaleSampleFragment]
    "Get a Sample by ID\n    \n    Returns a single Sample by ID. If the user does not have access\n    to the Sample, an error will be raised.\n    "

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = 'fragment MultiScaleSample on Sample {\n  id\n  name\n  representations(tags: ["multiscale"]) {\n    id\n    store\n    derived(ordering: "-meta_multiscale_depth") {\n      store\n    }\n  }\n}\n\nquery expand_multiscale($id: ID!) {\n  sample(id: $id) {\n    ...MultiScaleSample\n  }\n}'


class Get_roisQuery(BaseModel):
    rois: Optional[Tuple[Optional[ROIFragment], ...]]
    "All Rois\n    \n    This query returns all Rois that are stored on the platform\n    depending on the user's permissions. Generally, this query will return\n    all Rois that the user has access to. If the user is an amdin\n    or superuser, all Rois will be returned."

    class Arguments(BaseModel):
        representation: ID
        type: Optional[List[Optional[RoiTypeInput]]] = Field(default=None)

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  vectors {\n    x\n    y\n    z\n    t\n    c\n  }\n  type\n  representation {\n    id\n  }\n  creator {\n    id\n    color\n  }\n}\n\nquery get_rois($representation: ID!, $type: [RoiTypeInput]) {\n  rois(representation: $representation, type: $type) {\n    ...ROI\n  }\n}"


class Get_roiQuery(BaseModel):
    roi: Optional[ROIFragment]
    'Get a single Roi by ID"\n    \n    Returns a single Roi by ID. If the user does not have access\n    to the Roi, an error will be raised.'

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  vectors {\n    x\n    y\n    z\n    t\n    c\n  }\n  type\n  representation {\n    id\n  }\n  creator {\n    id\n    color\n  }\n}\n\nquery get_roi($id: ID!) {\n  roi(id: $id) {\n    ...ROI\n  }\n}"


class Search_roisQueryOptions(ROI, BaseModel):
    """A ROI is a region of interest in a representation.

    This region is to be regarded as a view on the representation. Depending
    on the implementatoin (type) of the ROI, the view can be constructed
    differently. For example, a rectangular ROI can be constructed by cropping
    the representation according to its 2 vectors. while a polygonal ROI can be constructed by masking the
    representation with the polygon.

    The ROI can also store a name and a description. This is used to display the ROI in the UI.

    """

    typename: Optional[Literal["ROI"]] = Field(alias="__typename", exclude=True)
    label: ID
    value: ID

    class Config:
        frozen = True


class Search_roisQuery(BaseModel):
    options: Optional[Tuple[Optional[Search_roisQueryOptions], ...]]
    "All Rois\n    \n    This query returns all Rois that are stored on the platform\n    depending on the user's permissions. Generally, this query will return\n    all Rois that the user has access to. If the user is an amdin\n    or superuser, all Rois will be returned."

    class Arguments(BaseModel):
        search: str
        values: Optional[List[Optional[ID]]] = Field(default=None)

    class Meta:
        document = "query search_rois($search: String!, $values: [ID]) {\n  options: rois(repname: $search, ids: $values) {\n    label: id\n    value: id\n  }\n}"


class Get_multiscale_repQuery(BaseModel):
    representation: Optional[MultiScaleRepresentationFragment]
    "Get a single Representation by ID\n\n    Returns a single Representation by ID. If the user does not have access\n    to the Representation, an error will be raised.\n    "

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = 'fragment MultiScaleRepresentation on Representation {\n  derived(tags: ["multiscale"]) {\n    name\n    tags\n    meta\n    store\n  }\n}\n\nquery get_multiscale_rep($id: ID!) {\n  representation(id: $id) {\n    ...MultiScaleRepresentation\n  }\n}'


class Get_representationQuery(BaseModel):
    representation: Optional[RepresentationFragment]
    "Get a single Representation by ID\n\n    Returns a single Representation by ID. If the user does not have access\n    to the Representation, an error will be raised.\n    "

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Representation on Representation {\n  sample {\n    id\n    name\n  }\n  id\n  store\n  variety\n  name\n  omero {\n    scale\n  }\n}\n\nquery get_representation($id: ID!) {\n  representation(id: $id) {\n    ...Representation\n  }\n}"


class Get_representation_and_maskQuery(BaseModel):
    representation: Optional[RepresentationAndMaskFragment]
    "Get a single Representation by ID\n\n    Returns a single Representation by ID. If the user does not have access\n    to the Representation, an error will be raised.\n    "

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment RepresentationAndMask on Representation {\n  sample {\n    id\n    name\n  }\n  id\n  store\n  variety\n  name\n  derived(variety: MASK) {\n    id\n    store\n    variety\n    name\n  }\n  omero {\n    scale\n  }\n}\n\nquery get_representation_and_mask($id: ID!) {\n  representation(id: $id) {\n    ...RepresentationAndMask\n  }\n}"


class Get_some_representationsQuery(BaseModel):
    representations: Optional[Tuple[Optional[ListRepresentationFragment], ...]]
    "All Representations\n\n    This query returns all Representations that are stored on the platform\n    depending on the user's permissions. Generally, this query will return\n    all Representations that the user has access to. If the user is an amdin\n    or superuser, all Representations will be returned."

    class Arguments(BaseModel):
        pass

    class Meta:
        document = 'fragment ListRepresentation on Representation {\n  id\n  name\n  sample {\n    id\n    name\n  }\n}\n\nquery get_some_representations {\n  representations(limit: 10, order: "-created_at") {\n    ...ListRepresentation\n  }\n}'


class DetailRepQuery(BaseModel):
    representation: Optional[DetailRepresentationFragment]
    "Get a single Representation by ID\n\n    Returns a single Representation by ID. If the user does not have access\n    to the Representation, an error will be raised.\n    "

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment DetailRepresentation on Representation {\n  sample {\n    id\n    name\n  }\n  id\n  store\n  shape\n  variety\n  name\n  omero {\n    physicalSize {\n      x\n      y\n      z\n    }\n    positions {\n      name\n      id\n      x\n      y\n      z\n      stage {\n        name\n        id\n      }\n    }\n    timepoints {\n      name\n      id\n      era {\n        name\n        id\n      }\n    }\n    views {\n      channel {\n        name\n        id\n      }\n      position {\n        name\n        id\n        x\n        y\n        z\n      }\n      timepoint {\n        id\n      }\n    }\n  }\n  metrics(flatten: 3) {\n    id\n    key\n    value\n    representation {\n      id\n    }\n  }\n  derived(flatten: 3) {\n    id\n    name\n    store\n  }\n}\n\nquery DetailRep($id: ID!) {\n  representation(id: $id) {\n    ...DetailRepresentation\n  }\n}"


async def awatch_rois(
    representation: ID, rath: MikroRath = None
) -> AsyncIterator[Optional[Watch_roisSubscriptionRois]]:
    """watch_rois



    Arguments:
        representation (ID): representation
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[Watch_roisSubscriptionRois]"""
    async for event in asubscribe(
        Watch_roisSubscription, {"representation": representation}, rath=rath
    ):
        yield event.rois


def watch_rois(
    representation: ID, rath: MikroRath = None
) -> Iterator[Optional[Watch_roisSubscriptionRois]]:
    """watch_rois



    Arguments:
        representation (ID): representation
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[Watch_roisSubscriptionRois]"""
    for event in subscribe(
        Watch_roisSubscription, {"representation": representation}, rath=rath
    ):
        yield event.rois


async def acreate_roi(
    representation: ID,
    vectors: List[Optional[InputVector]],
    type: RoiTypeInput,
    creator: Optional[ID] = None,
    rath: MikroRath = None,
) -> Optional[ROIFragment]:
    """create_roi


     createROI: A ROI is a region of interest in a representation.

        This region is to be regarded as a view on the representation. Depending
        on the implementatoin (type) of the ROI, the view can be constructed
        differently. For example, a rectangular ROI can be constructed by cropping
        the representation according to its 2 vectors. while a polygonal ROI can be constructed by masking the
        representation with the polygon.

        The ROI can also store a name and a description. This is used to display the ROI in the UI.




    Arguments:
        representation (ID): representation
        vectors (List[Optional[InputVector]]): vectors
        type (RoiTypeInput): type
        creator (Optional[ID], optional): creator.
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[ROIFragment]"""
    return (
        await aexecute(
            Create_roiMutation,
            {
                "representation": representation,
                "vectors": vectors,
                "creator": creator,
                "type": type,
            },
            rath=rath,
        )
    ).create_roi


def create_roi(
    representation: ID,
    vectors: List[Optional[InputVector]],
    type: RoiTypeInput,
    creator: Optional[ID] = None,
    rath: MikroRath = None,
) -> Optional[ROIFragment]:
    """create_roi


     createROI: A ROI is a region of interest in a representation.

        This region is to be regarded as a view on the representation. Depending
        on the implementatoin (type) of the ROI, the view can be constructed
        differently. For example, a rectangular ROI can be constructed by cropping
        the representation according to its 2 vectors. while a polygonal ROI can be constructed by masking the
        representation with the polygon.

        The ROI can also store a name and a description. This is used to display the ROI in the UI.




    Arguments:
        representation (ID): representation
        vectors (List[Optional[InputVector]]): vectors
        type (RoiTypeInput): type
        creator (Optional[ID], optional): creator.
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[ROIFragment]"""
    return execute(
        Create_roiMutation,
        {
            "representation": representation,
            "vectors": vectors,
            "creator": creator,
            "type": type,
        },
        rath=rath,
    ).create_roi


async def adelete_roi(
    id: ID, rath: MikroRath = None
) -> Optional[Delete_roiMutationDeleteroi]:
    """delete_roi



    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[Delete_roiMutationDeleteroi]"""
    return (await aexecute(Delete_roiMutation, {"id": id}, rath=rath)).delete_roi


def delete_roi(id: ID, rath: MikroRath = None) -> Optional[Delete_roiMutationDeleteroi]:
    """delete_roi



    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[Delete_roiMutationDeleteroi]"""
    return execute(Delete_roiMutation, {"id": id}, rath=rath).delete_roi


async def aget_label_for(
    representation: ID, instance: int, rath: MikroRath = None
) -> Optional[DetailLabelFragment]:
    """get_label_for


     labelFor: A Label is a trough model for image and features.

        Its map an instance value of a representation
        (e.g. a pixel value of a segmentation mask) to a set of corresponding features of the segmented
        class instance.

        There can only be one label per representation and class instance. You can then attach
        features to the label.





    Arguments:
        representation (ID): representation
        instance (int): instance
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[DetailLabelFragment]"""
    return (
        await aexecute(
            Get_label_forQuery,
            {"representation": representation, "instance": instance},
            rath=rath,
        )
    ).label_for


def get_label_for(
    representation: ID, instance: int, rath: MikroRath = None
) -> Optional[DetailLabelFragment]:
    """get_label_for


     labelFor: A Label is a trough model for image and features.

        Its map an instance value of a representation
        (e.g. a pixel value of a segmentation mask) to a set of corresponding features of the segmented
        class instance.

        There can only be one label per representation and class instance. You can then attach
        features to the label.





    Arguments:
        representation (ID): representation
        instance (int): instance
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[DetailLabelFragment]"""
    return execute(
        Get_label_forQuery,
        {"representation": representation, "instance": instance},
        rath=rath,
    ).label_for


async def aget_image_stage(
    id: ID, limit: Optional[int] = None, rath: MikroRath = None
) -> Optional[Get_image_stageQueryStage]:
    """get_image_stage


     stage: An Stage is a set of positions that share a common space on a microscope and can
        be use to translate.





    Arguments:
        id (ID): id
        limit (Optional[int], optional): limit.
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[Get_image_stageQueryStage]"""
    return (
        await aexecute(Get_image_stageQuery, {"id": id, "limit": limit}, rath=rath)
    ).stage


def get_image_stage(
    id: ID, limit: Optional[int] = None, rath: MikroRath = None
) -> Optional[Get_image_stageQueryStage]:
    """get_image_stage


     stage: An Stage is a set of positions that share a common space on a microscope and can
        be use to translate.





    Arguments:
        id (ID): id
        limit (Optional[int], optional): limit.
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[Get_image_stageQueryStage]"""
    return execute(Get_image_stageQuery, {"id": id, "limit": limit}, rath=rath).stage


async def aexpand_multiscale(
    id: ID, rath: MikroRath = None
) -> Optional[MultiScaleSampleFragment]:
    """expand_multiscale


     sample: Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure), was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample


    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[MultiScaleSampleFragment]"""
    return (await aexecute(Expand_multiscaleQuery, {"id": id}, rath=rath)).sample


def expand_multiscale(
    id: ID, rath: MikroRath = None
) -> Optional[MultiScaleSampleFragment]:
    """expand_multiscale


     sample: Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure), was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample


    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[MultiScaleSampleFragment]"""
    return execute(Expand_multiscaleQuery, {"id": id}, rath=rath).sample


async def aget_rois(
    representation: ID,
    type: Optional[List[Optional[RoiTypeInput]]] = None,
    rath: MikroRath = None,
) -> Optional[List[Optional[ROIFragment]]]:
    """get_rois


     rois: A ROI is a region of interest in a representation.

        This region is to be regarded as a view on the representation. Depending
        on the implementatoin (type) of the ROI, the view can be constructed
        differently. For example, a rectangular ROI can be constructed by cropping
        the representation according to its 2 vectors. while a polygonal ROI can be constructed by masking the
        representation with the polygon.

        The ROI can also store a name and a description. This is used to display the ROI in the UI.




    Arguments:
        representation (ID): representation
        type (Optional[List[Optional[RoiTypeInput]]], optional): type.
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[List[Optional[ROIFragment]]]"""
    return (
        await aexecute(
            Get_roisQuery, {"representation": representation, "type": type}, rath=rath
        )
    ).rois


def get_rois(
    representation: ID,
    type: Optional[List[Optional[RoiTypeInput]]] = None,
    rath: MikroRath = None,
) -> Optional[List[Optional[ROIFragment]]]:
    """get_rois


     rois: A ROI is a region of interest in a representation.

        This region is to be regarded as a view on the representation. Depending
        on the implementatoin (type) of the ROI, the view can be constructed
        differently. For example, a rectangular ROI can be constructed by cropping
        the representation according to its 2 vectors. while a polygonal ROI can be constructed by masking the
        representation with the polygon.

        The ROI can also store a name and a description. This is used to display the ROI in the UI.




    Arguments:
        representation (ID): representation
        type (Optional[List[Optional[RoiTypeInput]]], optional): type.
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[List[Optional[ROIFragment]]]"""
    return execute(
        Get_roisQuery, {"representation": representation, "type": type}, rath=rath
    ).rois


async def aget_roi(id: ID, rath: MikroRath = None) -> Optional[ROIFragment]:
    """get_roi


     roi: A ROI is a region of interest in a representation.

        This region is to be regarded as a view on the representation. Depending
        on the implementatoin (type) of the ROI, the view can be constructed
        differently. For example, a rectangular ROI can be constructed by cropping
        the representation according to its 2 vectors. while a polygonal ROI can be constructed by masking the
        representation with the polygon.

        The ROI can also store a name and a description. This is used to display the ROI in the UI.




    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[ROIFragment]"""
    return (await aexecute(Get_roiQuery, {"id": id}, rath=rath)).roi


def get_roi(id: ID, rath: MikroRath = None) -> Optional[ROIFragment]:
    """get_roi


     roi: A ROI is a region of interest in a representation.

        This region is to be regarded as a view on the representation. Depending
        on the implementatoin (type) of the ROI, the view can be constructed
        differently. For example, a rectangular ROI can be constructed by cropping
        the representation according to its 2 vectors. while a polygonal ROI can be constructed by masking the
        representation with the polygon.

        The ROI can also store a name and a description. This is used to display the ROI in the UI.




    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[ROIFragment]"""
    return execute(Get_roiQuery, {"id": id}, rath=rath).roi


async def asearch_rois(
    search: str, values: Optional[List[Optional[ID]]] = None, rath: MikroRath = None
) -> Optional[List[Optional[Search_roisQueryOptions]]]:
    """search_rois


     options: A ROI is a region of interest in a representation.

        This region is to be regarded as a view on the representation. Depending
        on the implementatoin (type) of the ROI, the view can be constructed
        differently. For example, a rectangular ROI can be constructed by cropping
        the representation according to its 2 vectors. while a polygonal ROI can be constructed by masking the
        representation with the polygon.

        The ROI can also store a name and a description. This is used to display the ROI in the UI.




    Arguments:
        search (str): search
        values (Optional[List[Optional[ID]]], optional): values.
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[List[Optional[Search_roisQueryRois]]]"""
    return (
        await aexecute(
            Search_roisQuery, {"search": search, "values": values}, rath=rath
        )
    ).rois


def search_rois(
    search: str, values: Optional[List[Optional[ID]]] = None, rath: MikroRath = None
) -> Optional[List[Optional[Search_roisQueryOptions]]]:
    """search_rois


     options: A ROI is a region of interest in a representation.

        This region is to be regarded as a view on the representation. Depending
        on the implementatoin (type) of the ROI, the view can be constructed
        differently. For example, a rectangular ROI can be constructed by cropping
        the representation according to its 2 vectors. while a polygonal ROI can be constructed by masking the
        representation with the polygon.

        The ROI can also store a name and a description. This is used to display the ROI in the UI.




    Arguments:
        search (str): search
        values (Optional[List[Optional[ID]]], optional): values.
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[List[Optional[Search_roisQueryRois]]]"""
    return execute(
        Search_roisQuery, {"search": search, "values": values}, rath=rath
    ).rois


async def aget_multiscale_rep(
    id: ID, rath: MikroRath = None
) -> Optional[MultiScaleRepresentationFragment]:
    """get_multiscale_rep


     representation: A Representation is 5-dimensional representation of an image

        Mikro stores each image as sa 5-dimensional representation. The dimensions are:
        - t: time
        - c: channel
        - z: z-stack
        - x: x-dimension
        - y: y-dimension

        This ensures a unified api for all images, regardless of their original dimensions. Another main
        determining factor for a representation is its variety:
        A representation can be a raw image representating voxels (VOXEL)
        or a segmentation mask representing instances of a class. (MASK)
        It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

        # Meta

        Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


        #Origins and Derivations

        Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
        Both are encapsulaed in the origins and derived fields.

        Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
        Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
        File and Rois that are used to create images are saved in the file origins and roi origins repectively.





    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[MultiScaleRepresentationFragment]"""
    return (
        await aexecute(Get_multiscale_repQuery, {"id": id}, rath=rath)
    ).representation


def get_multiscale_rep(
    id: ID, rath: MikroRath = None
) -> Optional[MultiScaleRepresentationFragment]:
    """get_multiscale_rep


     representation: A Representation is 5-dimensional representation of an image

        Mikro stores each image as sa 5-dimensional representation. The dimensions are:
        - t: time
        - c: channel
        - z: z-stack
        - x: x-dimension
        - y: y-dimension

        This ensures a unified api for all images, regardless of their original dimensions. Another main
        determining factor for a representation is its variety:
        A representation can be a raw image representating voxels (VOXEL)
        or a segmentation mask representing instances of a class. (MASK)
        It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

        # Meta

        Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


        #Origins and Derivations

        Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
        Both are encapsulaed in the origins and derived fields.

        Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
        Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
        File and Rois that are used to create images are saved in the file origins and roi origins repectively.





    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[MultiScaleRepresentationFragment]"""
    return execute(Get_multiscale_repQuery, {"id": id}, rath=rath).representation


async def aget_representation(
    id: ID, rath: MikroRath = None
) -> Optional[RepresentationFragment]:
    """get_representation


     representation: A Representation is 5-dimensional representation of an image

        Mikro stores each image as sa 5-dimensional representation. The dimensions are:
        - t: time
        - c: channel
        - z: z-stack
        - x: x-dimension
        - y: y-dimension

        This ensures a unified api for all images, regardless of their original dimensions. Another main
        determining factor for a representation is its variety:
        A representation can be a raw image representating voxels (VOXEL)
        or a segmentation mask representing instances of a class. (MASK)
        It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

        # Meta

        Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


        #Origins and Derivations

        Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
        Both are encapsulaed in the origins and derived fields.

        Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
        Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
        File and Rois that are used to create images are saved in the file origins and roi origins repectively.





    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[RepresentationFragment]"""
    return (
        await aexecute(Get_representationQuery, {"id": id}, rath=rath)
    ).representation


def get_representation(
    id: ID, rath: MikroRath = None
) -> Optional[RepresentationFragment]:
    """get_representation


     representation: A Representation is 5-dimensional representation of an image

        Mikro stores each image as sa 5-dimensional representation. The dimensions are:
        - t: time
        - c: channel
        - z: z-stack
        - x: x-dimension
        - y: y-dimension

        This ensures a unified api for all images, regardless of their original dimensions. Another main
        determining factor for a representation is its variety:
        A representation can be a raw image representating voxels (VOXEL)
        or a segmentation mask representing instances of a class. (MASK)
        It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

        # Meta

        Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


        #Origins and Derivations

        Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
        Both are encapsulaed in the origins and derived fields.

        Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
        Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
        File and Rois that are used to create images are saved in the file origins and roi origins repectively.





    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[RepresentationFragment]"""
    return execute(Get_representationQuery, {"id": id}, rath=rath).representation


async def aget_representation_and_mask(
    id: ID, rath: MikroRath = None
) -> Optional[RepresentationAndMaskFragment]:
    """get_representation_and_mask


     representation: A Representation is 5-dimensional representation of an image

        Mikro stores each image as sa 5-dimensional representation. The dimensions are:
        - t: time
        - c: channel
        - z: z-stack
        - x: x-dimension
        - y: y-dimension

        This ensures a unified api for all images, regardless of their original dimensions. Another main
        determining factor for a representation is its variety:
        A representation can be a raw image representating voxels (VOXEL)
        or a segmentation mask representing instances of a class. (MASK)
        It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

        # Meta

        Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


        #Origins and Derivations

        Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
        Both are encapsulaed in the origins and derived fields.

        Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
        Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
        File and Rois that are used to create images are saved in the file origins and roi origins repectively.





    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[RepresentationAndMaskFragment]"""
    return (
        await aexecute(Get_representation_and_maskQuery, {"id": id}, rath=rath)
    ).representation


def get_representation_and_mask(
    id: ID, rath: MikroRath = None
) -> Optional[RepresentationAndMaskFragment]:
    """get_representation_and_mask


     representation: A Representation is 5-dimensional representation of an image

        Mikro stores each image as sa 5-dimensional representation. The dimensions are:
        - t: time
        - c: channel
        - z: z-stack
        - x: x-dimension
        - y: y-dimension

        This ensures a unified api for all images, regardless of their original dimensions. Another main
        determining factor for a representation is its variety:
        A representation can be a raw image representating voxels (VOXEL)
        or a segmentation mask representing instances of a class. (MASK)
        It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

        # Meta

        Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


        #Origins and Derivations

        Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
        Both are encapsulaed in the origins and derived fields.

        Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
        Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
        File and Rois that are used to create images are saved in the file origins and roi origins repectively.





    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[RepresentationAndMaskFragment]"""
    return execute(
        Get_representation_and_maskQuery, {"id": id}, rath=rath
    ).representation


async def aget_some_representations(
    rath: MikroRath = None,
) -> Optional[List[Optional[ListRepresentationFragment]]]:
    """get_some_representations


     representations: A Representation is 5-dimensional representation of an image

        Mikro stores each image as sa 5-dimensional representation. The dimensions are:
        - t: time
        - c: channel
        - z: z-stack
        - x: x-dimension
        - y: y-dimension

        This ensures a unified api for all images, regardless of their original dimensions. Another main
        determining factor for a representation is its variety:
        A representation can be a raw image representating voxels (VOXEL)
        or a segmentation mask representing instances of a class. (MASK)
        It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

        # Meta

        Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


        #Origins and Derivations

        Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
        Both are encapsulaed in the origins and derived fields.

        Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
        Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
        File and Rois that are used to create images are saved in the file origins and roi origins repectively.





    Arguments:
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[List[Optional[ListRepresentationFragment]]]"""
    return (
        await aexecute(Get_some_representationsQuery, {}, rath=rath)
    ).representations


def get_some_representations(
    rath: MikroRath = None,
) -> Optional[List[Optional[ListRepresentationFragment]]]:
    """get_some_representations


     representations: A Representation is 5-dimensional representation of an image

        Mikro stores each image as sa 5-dimensional representation. The dimensions are:
        - t: time
        - c: channel
        - z: z-stack
        - x: x-dimension
        - y: y-dimension

        This ensures a unified api for all images, regardless of their original dimensions. Another main
        determining factor for a representation is its variety:
        A representation can be a raw image representating voxels (VOXEL)
        or a segmentation mask representing instances of a class. (MASK)
        It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

        # Meta

        Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


        #Origins and Derivations

        Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
        Both are encapsulaed in the origins and derived fields.

        Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
        Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
        File and Rois that are used to create images are saved in the file origins and roi origins repectively.





    Arguments:
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[List[Optional[ListRepresentationFragment]]]"""
    return execute(Get_some_representationsQuery, {}, rath=rath).representations


async def adetail_rep(
    id: ID, rath: MikroRath = None
) -> Optional[DetailRepresentationFragment]:
    """DetailRep


     representation: A Representation is 5-dimensional representation of an image

        Mikro stores each image as sa 5-dimensional representation. The dimensions are:
        - t: time
        - c: channel
        - z: z-stack
        - x: x-dimension
        - y: y-dimension

        This ensures a unified api for all images, regardless of their original dimensions. Another main
        determining factor for a representation is its variety:
        A representation can be a raw image representating voxels (VOXEL)
        or a segmentation mask representing instances of a class. (MASK)
        It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

        # Meta

        Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


        #Origins and Derivations

        Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
        Both are encapsulaed in the origins and derived fields.

        Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
        Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
        File and Rois that are used to create images are saved in the file origins and roi origins repectively.





    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[DetailRepresentationFragment]"""
    return (await aexecute(DetailRepQuery, {"id": id}, rath=rath)).representation


def detail_rep(
    id: ID, rath: MikroRath = None
) -> Optional[DetailRepresentationFragment]:
    """DetailRep


     representation: A Representation is 5-dimensional representation of an image

        Mikro stores each image as sa 5-dimensional representation. The dimensions are:
        - t: time
        - c: channel
        - z: z-stack
        - x: x-dimension
        - y: y-dimension

        This ensures a unified api for all images, regardless of their original dimensions. Another main
        determining factor for a representation is its variety:
        A representation can be a raw image representating voxels (VOXEL)
        or a segmentation mask representing instances of a class. (MASK)
        It can also representate a human perception of the image (RGB) or a human perception of the mask (RGBMASK)

        # Meta

        Meta information is stored in the omero field which gives access to the omero-meta data. Refer to the omero documentation for more information.


        #Origins and Derivations

        Images can be filtered, which means that a new representation is created from the other (original) representations. This new representation is then linked to the original representations. This way, we can always trace back to the original representation.
        Both are encapsulaed in the origins and derived fields.

        Representations belong to *one* sample. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample
        Each iamge has also a name, which is used to identify the image. The name is unique within a sample.
        File and Rois that are used to create images are saved in the file origins and roi origins repectively.





    Arguments:
        id (ID): id
        rath (mikro.rath.MikroRath, optional): The mikro rath client

    Returns:
        Optional[DetailRepresentationFragment]"""
    return execute(DetailRepQuery, {"id": id}, rath=rath).representation


DescendendInput.update_forward_refs()
OmeroRepresentationInput.update_forward_refs()
