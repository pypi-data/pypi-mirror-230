"""
Pydantic models related to the input specifications of an MLModel.
"""

from pathlib import Path
from typing import List, Literal, Union

from pydantic import BaseModel, Field


class ZeroToOneScaler(BaseModel):
    """
    Normalize the input image to [0, 1] range.
    """

    name: Literal["ZeroToOne"] = Field("ZeroToOne", title="Scale input to range [0,1]")


class MinusOneToOneScaler(BaseModel):
    """
    Normalize the input image to [-1, 1] range with 0 mean.
    """

    name: Literal["MinusOneToOne"] = Field("MinusOneToOne", title="Scale input to range [-1, 1]")


class ImageNetPresetScaler(BaseModel):
    """
    Standardize the input image with ImageNet mean and standard deviation.
    """

    name: Literal["ImageNetScaler"] = Field("ImageNetScaler", title="ImageNet Standardization")
    data_mean: List[float] = Field(default=[0.485, 0.456, 0.406], title="Mean", hidden=True)
    data_std: List[float] = Field(
        default=[0.229, 0.224, 0.225], title="Standard Deviation", hidden=True
    )


class RGBCustomScaler(BaseModel):
    """
    Standardize the input image with the given per-channel mean and standard
    deviation values.
    """

    name: Literal["RGBCustom"] = Field("RGBCustom", title="Custom Standardization")
    data_mean: List[float] = Field(default=[0.0, 0.0, 0.0], title="Mean")
    data_std: List[float] = Field(default=[1.0, 1.0, 1.0], title="Standard Deviation")


class GrayscaleCustomScaler(BaseModel):
    """
    Standardize the input image with the given mean and standard deviation.
    """

    name: Literal["GrayScaleCustom"] = Field("GrayScaleCustom", title="Custom Standardization")
    data_mean: float = Field(default=0.0, title="Mean")
    data_std: float = Field(default=1.0, gt=0.0, title="Standard Deviation")


class ImageInputConfig(BaseModel):
    """
    Configuration of input images.
    """

    image_type: Literal["grayscale", "color"] = Field(
        default="color", title="Color type of the input images."
    )
    width: int = Field(title="Width of the input images.")
    height: int = Field(title="Height of the input images.")
    input_dim_order: Literal["chw", "cwh", "hwc", "whc"] = Field(
        default="hwc", title="Dimension order of the input images."
    )  # allow any combination != 'xcx'


class Split(BaseModel):
    """
    Pre-tokenizer that splits text input before tokenization.
    """

    convert_to_lower_case: bool = Field(
        default=True,
        description=(
            "Whether to convert the text input to lower case. If True, 'This is A sentence' -> "
            "'this is a sentence'. If False, 'This is A Sentence' -> 'This is A sentence'."
        ),
        title="Convert to lower case.",
    )
    split_by_whitespace: bool = Field(
        default=True,
        description=(
            "Whether to separate the input text into words. If True, 'this is a sentence' -> "
            "'this', 'is', 'a', 'sentence'. If False, 'this is a sentence' -> 'this is a "
            "sentence'."
        ),
        title="Split by whitespace.",
    )
    keep_punctuation: bool = Field(
        default=True,
        description=(
            "Whether to keep punctuation (.,;:!?()) as separate tokens. If True, 'hello! this is a "
            "sentence.' -> 'hello', '!', 'this', 'is', 'a', 'sentence', '.' If False, 'hello! this "
            "is a sentence.' -> 'hello', 'this', 'is', 'a', 'sentence'"
        ),
        title="Keep punctuation.",
    )


class ByteLevel(BaseModel):
    """
    Pre-tokenizer that encodes each byte value to a unique character.

    This is a wrapper of the Hugging Face implementation of the Byte
    Level Pre-Tokenizer.
    """


class WordLevel(BaseModel):
    """
    Word-Level tokenizer that maps each token to an ID according to a
    vocabulary.
    """

    unk_token: str = Field(
        default="[UNK]",
        description="Symbol to represent tokens that are not in the vocabulary.",
        title="Unknown token.",
    )
    vocab: Union[str, Path] = Field(
        ...,
        description=(
            "The expected format is a JSON representation of a dictionary where the keys are the "
            "symbols in the vocabulary (strings) and the values are the corresponding IDs "
            '(integers), e.g.: {"hello": 1, "world": 2, "[UNK]": 3}'  # noqa: FS003
        ),
        title="Vocabulary.",
    )


class BytePairEncoding(BaseModel):
    """
    Byte-Pair Encoding (BPE) tokenizer that first creates a 'merge list' and an
    according vocabulary by iteratively creating entries from merging the most
    frequent symbol pairs.

    Then, during tokenization, tokens are first merged according to the
    'merge list' and then mapped to IDs using the vocabulary.
    """

    unk_token: str = Field(
        default="<unk>",
        description="Symbol to represent tokens that are not in the vocabulary.",
        title="Unknown token.",
    )
    vocab: Union[str, Path] = Field(
        ...,
        description=(
            "The expected format is a JSON representation of a dictionary where the keys are the "
            "symbols in the vocabulary (strings) and the values are the corresponding IDs "
            '(integers), e.g.: {"hello": 1, "world": 2, "[UNK]": 3}'  # noqa: FS003
        ),
        title="Vocabulary.",
    )
    merges: Union[str, Path] = Field(
        ...,
        description=(
            "Symbol pairs to be merged during Byte-Pair Encoding. The expected format is a text "
            "where each line contains one pair of symbols, i.e.:\na b\nc d\ne f\n"
        ),
        title="Merges.",
    )
