"""
Pydantic models related to the specification of the output of an MLModel.
"""
from typing import Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Literal

from aidkit_client._endpoints.models import BoundingBoxFormatType

_BOUNDING_BOXES_FORMATS = {
    "xyxy": BoundingBoxFormatType.xyxy,
    "yxyx": BoundingBoxFormatType.yxyx,
    "xywh": BoundingBoxFormatType.xywh,
    "ccwh": BoundingBoxFormatType.ccwh,
}


class DictionaryOfTensors(BaseModel):
    """
    Dictionary of tensors.
    """

    output_target: str = Field(title="Output target class.")


class ClassificationOutputFormat(BaseModel):
    """
    Output format of classification models.
    """

    format: Union[Literal["single_tensor"], DictionaryOfTensors] = Field(
        default=Literal["single_tensor"], title="Format of the classification model output."
    )


class SegmentationOutputFormat(BaseModel):
    """
    Output format of image segmentation models.
    """

    format: Union[Literal["single_tensor"], DictionaryOfTensors] = Field(
        default=Literal["single_tensor"], title="Format of the classification model output."
    )
    output_dim_order: Literal["chw", "cwh", "hwc", "whc"] = Field(
        default="hwc", title="Dimension order of the output images."
    )  # allow any combination != 'xcx'


class BoundingBoxesFormat(BaseModel):
    """
    Dictionary representing the format of the boxes given as output by an
    object detection model.
    """

    identifier: Union[str, int] = Field(
        title="Boxes identifier",
        description=(
            "Pointer to the bounding boxes in the model output. It should be a string key if the "
            "output format is specified as a dictionary and an integer index if it is a sequence "
            "of tensors."
        ),
    )
    shape: Literal["boxes_coordinates", "coordinates_boxes"] = Field(
        default="boxes_coordinates",
        title="Bounding boxes shape",
        description=(
            "Order in which the dimensions of the bounding boxes are given. Can be either boxes "
            "first ('boxes_coordinates') or coordinates first ('coordinates_boxes')."
        ),
    )
    format: Literal["xyxy", "yxyx", "xywh", "ccwh"] = Field(
        title="Bounding box format",
        description=(
            "Format of the bounding boxes. These are always represented by a 4-tuple "
            "corresponding to either the coordinates of 2 points or to the coordinates of one "
            "point and the width and height of the box. `min` is the point with minimal x and y "
            "coordinate. `max` is the point with maximal x and y coordinate. `c` is the center of "
            "the box. The options are: "
            "`xyxy`: (`x_min`, `y_min`, `x_max`, `y_max`). "
            "`yxyx`: (`y_min`, `x_min`, `y_max`, `x_max`). "
            "`xywh`: (`x_min`, `y_min`, `width`, `height`). "
            "`ccwh`: (`x_c`, `y_c`, `width`, `height`)."
        ),
    )


class NMSPostProcessor(BaseModel):
    """
    Apply non-max suppression to object proposals.
    """

    iou_threshold: float = Field(
        default=0.5,
        description="Overlapping boxes with IOU greater than this threshold will be discarded.",
        ge=0.0,
        le=1.0,
        title="IOU Threshold",
    )
    score_threshold: float = Field(
        default=0,
        description="Boxes with confidence below this threshold will be discarded.",
        title="Score Threshold",
    )
    class_to_suppress: Optional[int] = Field(
        default=None,
        description=(
            "A single class index. Boxes which are classified as this class are removed before "
            "non-max suppression. A typical choice is to select the index that refers to a "
            "'background' class."
        ),
        title="Class to suppress",
    )


class DetectionOutputFormat(BaseModel):
    """
    Object Detection output format.
    """

    boxes: BoundingBoxesFormat = Field(
        title="Boxes output format", description="Format that the boxes in the output respect."
    )
    scores_shape: Literal["boxes_classes", "classes_boxes"] = Field(
        title="Shape of the scores",
        description=(
            "Order in which the classes and the boxes appear in the output. Can be either boxes "
            "first ('boxes_classes') or classes first ('classes_boxes')."
        ),
        default="boxes_classes",
    )
    format: Literal["dictionary", "sequence"] = Field(
        default=Literal["dictionary"],
        title="Output format",
        description="Format of the detection model output.",
    )
    scores_identifier: Union[str, int] = Field(
        title="Scores identifier",
        description=(
            "Pointer to the differentiable output layer in shape `(batch size x bounding boxes x "
            "classes)` just before the NMS. It should be a string key if the output format "
            "is specified as a dictionary and an integer index if it is a sequence of tensors."
        ),
    )
    post_processing: Optional[NMSPostProcessor] = Field(
        title="Post processing",
        description="Post processing to apply to the results. Currently, only NMS is supported.",
    )
