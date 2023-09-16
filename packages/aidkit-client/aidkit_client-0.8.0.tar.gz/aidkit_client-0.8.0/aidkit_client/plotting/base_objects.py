"""
Functions to plot basic objects like tables and image comparisons.
"""

import colorsys
import difflib
import io
from math import ceil
from typing import Dict, List, Optional, Sequence, Set, Tuple, TypeVar, Union

import numpy as np
import PIL.Image
import PIL.ImageDraw
from ipywidgets import widgets
from matplotlib import colormaps
from matplotlib import pyplot as plt

from aidkit_client._endpoints.models import ImageObjectDetectionBoundingBox

T = TypeVar("T", str, PIL.Image.Image)


def display_table(
    data: Dict[str, List[Union[str, float, int]]],
    header: Optional[Sequence[Union[str, float, int]]] = None,
    highlight_row_header: Optional[Dict[str, str]] = None,
    highlight_cells: Optional[Dict[str, Dict[int, str]]] = None,
    table_width: int = 540,
) -> widgets.GridBox:
    """
    Create a table widget from a dictionary.

    :raises RuntimeError: If the header length and the data do not match.
    :param data: Dict containing the table values.
    :param header: Optional list of headers.
    :param highlight_row_header: Dict specifying which row headers to highlight in which color:
            access color as the following highlight_row_header[row_header].
    :param highlight_cells: Dict specifying which cells to highlight in which color:
            access color as the following highlight_cells[row_header][col].
    :param table_width: Width in pixels of the table. The columns size is
            allocated dynamically.
    :return: Widget containing the table.
    """
    items = []
    if header:
        items.append(widgets.Label(""))
        for _header in header:
            items.append(widgets.HTML(value=f"<b>{_header}</b>"))

    cols = 1 + len(list(data.values())[0])

    if header and cols != (len(header) + 1):
        raise RuntimeError("The length of the header as to match the data.")

    for key, value_list in data.items():
        header_html = f"<span style='display: inline-block; line-height: 1.2em'><b>{key}</b></span>"

        # add background color
        if highlight_row_header and key in highlight_row_header:
            header_html = (
                f"<span style='background-color:{highlight_row_header[key]};"
                "'>\u00A0\u00A0\u00A0\u00A0</span> " + header_html
            )
        items.append(widgets.HTML(value=header_html))

        for i, value in enumerate(value_list):
            if isinstance(value, dict):
                value_to_print = _pretty_print_dict(value)
            else:
                value_to_print = str(value)

            if highlight_cells:
                highlight = highlight_cells.get(key, {}).get(i, None)
                if highlight:
                    value_to_print = (
                        f"<span style='background-color:{highlight};'>" + value_to_print + "</span>"
                    )
            items.append(widgets.HTML(value=value_to_print))

    return widgets.GridBox(
        items,
        layout=widgets.Layout(
            grid_template_columns=f"180px repeat({cols-1},\
            {(table_width - 180)/(cols-1)}px)"
        ),
    )


def _pretty_print_dict(dictionary: Dict) -> str:
    """
    Pretty print a dictionary.

    :param dictionary: Dictionary to print.
    :return: String with html representation.
    """
    value_to_print = ""
    for key, value in dictionary.items():
        if isinstance(value, list):
            value_to_print += f"{key}: {str(value)[1:-1]}<br>"
        else:
            value_to_print += f"{key}: {value}<br>"
    return value_to_print


def display_warning_message(message: str) -> widgets.HTML:
    """
    Create a widget displaying a warning message.

    :param message: The warning message to display.
    :return: A HTML widget containing the warning message passed as argument.
    """
    warning_style = r"""
            color : peru;
            background-color : lightyellow;
            width : 586px;
            margin : 2px;
            padding  : 5px;
            line-height : normal
        """
    return widgets.HTML(value=f"<p style='{warning_style}'><b>Warning:</b> {message}</p>")


def display_observation(
    observation: T,
    title: Optional[str] = None,
    caption: Optional[List[Tuple[str, str]]] = None,
    width: Optional[int] = 300,
) -> Union[widgets.Image, widgets.HTML, widgets.VBox]:
    """
    Create a widget displaying a single observation.

    :param observation: Observation to display.
    :param title: Title to be displayed above the observation.
    :param caption: Caption to be displayed below the observation.
    :param width: Width of the image.
    :return: Widget containing the observation.
    """
    if isinstance(observation, str):
        observation_widget = widgets.HTML(value=observation)
    else:
        buff = io.BytesIO()
        observation.save(buff, format="png")
        observation_widget = widgets.Image(value=buff.getvalue(), width=width)

    widget_list = [observation_widget]

    if title:
        title_widget = widgets.HTML(value=title)
        widget_list = [title_widget] + widget_list

    if caption:
        caption_text = "<center>"
        for i, (key, value) in enumerate(caption):
            if i != 0:
                caption_text += "<br>"
            if len(key + value) > 30:
                caption_text += f'<span title="{value}"><b>{key}</b>: ...{value[-30:]}</b></span>'
            else:
                caption_text += f"<span><b>{key}</b>: {value}</b></span>"

        caption_text += "</center>"
        caption_widget = widgets.HTML(value=caption_text)
        widget_list.append(caption_widget)

    if len(widget_list) == 1:
        return widget_list[0]

    return widgets.VBox(widget_list)


def display_observation_difference(original: T, perturbed: T) -> widgets.VBox:
    """
    Create a widget displaying the difference of two observations of the same
    type depending on an interactive scalar, multiplying the difference.

    :param original: Original observation.
    :param perturbed: Perturbed observation.
    :return: Widget displaying the diff.
    """
    if isinstance(original, str):
        return display_static_observation_difference(original, perturbed)

    original = np.array(original)
    perturbed = np.array(perturbed)
    diff = np.abs(perturbed - original).astype(np.uint16)

    def _plot_img(scalar: widgets.IntSlider) -> None:
        curr = diff * scalar
        curr[curr > 255] = 255
        plt.imshow(curr, vmin=0, vmax=255)
        plt.title("Difference: Perturbation - Original")
        plt.axis("off")

    diff_slider = widgets.IntSlider(value=1, min=1, max=20, description="Scalar")
    interactive_function = widgets.interactive(_plot_img, scalar=diff_slider)
    interactive_function.update()
    return widgets.VBox(children=interactive_function.children)


def display_static_observation_difference(original: T, perturbed: T) -> widgets.VBox:
    """
    Create a widget displaying the difference of two observations of the same
    type.

    :param original: Original observation.
    :param perturbed: Perturbed observation.
    :return: Widget displaying the diff.
    """
    if isinstance(original, str):
        out_html_1 = ""
        out_html_2 = ""
        for character_diff in difflib.ndiff(original, perturbed):
            if character_diff[0] == " ":
                out_html_1 += character_diff[-1]
                out_html_2 += character_diff[-1]
            elif character_diff[0] == "-":
                out_html_1 += f'<FONT COLOR="#FF8000"><s>{character_diff[-1]}</s></FONT>'
            elif character_diff[0] == "+":

                out_html_2 += f'<FONT COLOR="0040FF">{character_diff[-1]}</FONT>'
        return widgets.VBox([widgets.HTML(value=out_html_1), widgets.HTML(value=out_html_2)])

    original = np.array(original)
    perturbed = np.array(perturbed)

    if original.shape != perturbed.shape and len(perturbed.shape) == 2:
        perturbed = np.stack((perturbed,) * 3, axis=-1)

    diff_array = np.abs(perturbed.astype(float) - original.astype(float))
    diff_array_normalized = diff_array * (255 / np.max(diff_array))
    diff = PIL.Image.fromarray(diff_array_normalized.astype("uint8"))

    buff = io.BytesIO()
    diff.save(buff, format="png")
    return widgets.VBox(
        [
            widgets.HTML(value="<b>Difference: Perturbation - Original</b>"),
            widgets.Image(
                value=buff.getvalue(),
                width=300,
                height=400,
            ),
            widgets.HTML(
                value='<FONT COLOR="#949191">The pixel values are \
                 normalized to the range [0, 1] for visibility.</FONT>'
            ),
        ]
    )


def blended_images_widget(
    backgrounds: List[PIL.Image.Image],
    foregrounds: List[PIL.Image.Image],
    titles: List[str],
    steps: int,
) -> Tuple[widgets.Stack, widgets.HBox]:
    """
    Display a list of images side by side and returns a slider that controls
    how visible the foreground images should be on top of the background ones.

    :param backgrounds: Images shown when the slider is set to 0.
    :param foregrounds: Images shown when the slider is set to 1.
    :param titles: Titles shown above the images.
    :param steps: Number of steps needed to go from the foreground images not being visible to them
        hiding the background images completely.
    :return: A stack widget with the images side by side for each step and a slider widget
        controlling which step is displayed.
    """
    # Add alpha channel to the images
    backgrounds_rgba = [background.convert("RGBA") for background in backgrounds]
    foregrounds_rgba = [foreground.convert("RGBA") for foreground in foregrounds]

    # Create widget lists that will be used in a stack widget. The value for the slider has to
    # Be created using a stack widget in order to display a percentage instead of a index.
    blended_images_widgets = []
    slider_legends = []

    for step in range(steps + 1):
        blended_images = []
        for background_rgba, foreground_rgba, title in zip(
            backgrounds_rgba, foregrounds_rgba, titles
        ):
            blended = PIL.Image.blend(background_rgba, foreground_rgba, alpha=step / steps)
            blended_images.append(display_observation(blended, title=f"<b>{title}</b>", width=250))

        slider_legends.append(widgets.HTML(value=f"{step / steps:.0%}"))
        blended_images_widgets.append(widgets.HBox(children=blended_images))

    # The slider has to be an integer slider to control the stack widget. By setting
    # "readout=False" we don't display its value directly. Instead we will replace it by another
    # widget that displays a percentage using the values in "slider_legends".
    class_prediction_opacity_slider = widgets.IntSlider(
        value=9, min=0, max=steps, step=1, continuous_update=False, readout=False
    )

    blended_images_stack = widgets.Stack(children=blended_images_widgets)
    widgets.jslink(
        (class_prediction_opacity_slider, "value"), (blended_images_stack, "selected_index")
    )

    slider_legends_stack = widgets.Stack(children=slider_legends)
    widgets.jslink(
        (class_prediction_opacity_slider, "value"), (slider_legends_stack, "selected_index")
    )

    class_prediction_opacity_slider_with_description = widgets.HBox(
        [widgets.Label("Labels Opacity:"), class_prediction_opacity_slider, slider_legends_stack]
    )

    return blended_images_stack, class_prediction_opacity_slider_with_description


def display_target_class_legend_widget(target_classes: List[dict]) -> widgets.HTML:
    """
    Display a widget containing a list of classes with their associated color.

    :param target_classes: List of dictionaries containing the name and the color of each class
         to display.
    :return: HTML widget with the list of classes.
    """
    target_classes_legend = """<style>
    .class_legend_element {
        background-color:#efefef;
        margin: 3px;
        padding-left: 5px;
        padding-right: 5px;
        float: left;

    .class_legend {
        display: block;
    }
    </style>
    <div class="class_legend">
    """
    for target_class in target_classes:
        color = target_class["color"]
        target_classes_legend += (
            '<span class="class_legend_element">'
            f'<span style="color:{color}; font-size: 16px">&#9632; </span>'
            f'{target_class["name"]}</span>'
        )
    target_classes_legend += "</div>"

    return widgets.HTML(value=target_classes_legend)


def display_semantic_segmentation_inference_widget(
    original: PIL.Image,
    perturbed: PIL.Image,
    original_prediction: PIL.Image,
    perturbed_prediction: PIL.Image,
    target_classes: List[dict],
) -> widgets.VBox:
    """
    Display a widget containing the prediction of a semantic segmentation
    model.

    :param original: Original observation.
    :param perturbed: The perturbed observation.
    :param original_prediction: An image representing the prediction of the model
        on the original image.
    :param perturbed_prediction: An image representing the prediction of the model
        on the perturbed image.
    :param target_classes: A dictionary containing the name and colors
        of the target classes.
    :return: A widget displaying the inference of the model.
    """
    target_class_legend_widget = display_target_class_legend_widget(target_classes)

    class_prediction_widget, class_prediction_opacity_slider = blended_images_widget(
        [original, perturbed],
        [original_prediction, perturbed_prediction],
        ["Prediction for original observation", "Prediction for perturbed observation"],
        10,
    )

    return widgets.VBox(
        [
            class_prediction_widget,
            target_class_legend_widget,
            class_prediction_opacity_slider,
        ]
    )


def generate_color_list(n: int) -> List[Tuple[int, int, int]]:
    """
    Generate a list of n colors obtained by sampling the HSV space uniformly.
    This produces colors that are distinct.

    :param n: Number of colors to return.
    :return: A list of colors in RGB.
    """
    hue_partition = np.linspace(0.0, 1.0, n + 1)[:n]
    saturation_modifier = np.tile([1.0, 0.5], ceil(n / 2))[:n]
    value_modifier = np.tile([1.0, 0.6], ceil(n / 2))[:n]
    hsv_colors = np.stack([hue_partition, saturation_modifier, value_modifier])

    def _hsv_to_rgb(hsv_color: np.ndarray) -> Tuple[int, int, int]:
        """
        Convert a numpy array representing a color in the HSV format to RGB.

        :param hsv_color: Numpy array of 3 elements representing a color in the HSV format.
        :return: Tuple representing the same color in RGB.
        """
        (red, green, blue) = colorsys.hsv_to_rgb(hsv_color[0], hsv_color[1], hsv_color[2])
        return (int(255 * red), int(255 * green), int(255 * blue))

    rgb_colors = np.apply_along_axis(_hsv_to_rgb, 1, hsv_colors.transpose([1, 0]))
    return list(rgb_colors)


def get_segmentation_prediction(
    inference_result: np.ndarray, class_colors: Optional[List[Tuple[int, int, int]]] = None
) -> Tuple[PIL.Image.Image, Set[int]]:
    """
    Generates an image where each class has its unique color.

    :param inference_result: A numpy array with shape `[r,c]` where `r` is the number of rows and
        `c` the number of columns.
    :param class_colors: Optional list containing the color associated with each class as a string.
         If not specified, a default color map is used.
    :return: A PIL Image where every pixel has the color of its class.
    """
    classes_present = set(np.unique(inference_result))

    if not class_colors:
        color_map = colormaps["gist_ncar"](inference_result, bytes=True)
        inference_image = PIL.Image.fromarray(np.uint8(color_map))

    else:
        colors_array = np.array(class_colors)

        def _class_index_to_color(array: np.ndarray) -> np.ndarray:
            return colors_array[array]

        rgb_inference = _class_index_to_color(inference_result).astype(np.uint8)
        inference_image = PIL.Image.fromarray(rgb_inference)

    return inference_image, classes_present


def display_object_detection_box_count_widget(
    original_detection_output: List[ImageObjectDetectionBoundingBox],
    perturbed_detection_output: List[ImageObjectDetectionBoundingBox],
    class_names: List[str],
    class_colors: List[str],
) -> widgets.GridBox:
    """
    Create a widget displaying the distribution of boxes in a table.

    :param original_detection_output: Object detection inference of the original observation.
    :param perturbed_detection_output: Object detection inference of the perturbed observation.
    :param class_names: List of all class names.
    :param class_colors: Dictionary maping a color to a class name.
    :return: Table widget.
    """
    box_table_1_counter: Dict[int, int] = {}
    for bbox in original_detection_output:
        box_table_1_counter[bbox.class_index] = box_table_1_counter.get(bbox.class_index, 0) + 1
    box_table_2_counter: Dict[int, int] = {}
    for bbox in perturbed_detection_output:
        box_table_2_counter[bbox.class_index] = box_table_2_counter.get(bbox.class_index, 0) + 1

    box_table_counter: Dict[str, List[Union[str, float, int]]] = {}
    highlights = {}
    for class_ in set(list(box_table_1_counter.keys()) + list(box_table_2_counter.keys())):
        box_table_counter[class_names[class_]] = [
            box_table_1_counter.get(class_, 0),
            box_table_2_counter.get(class_, 0),
        ]
        highlights[class_names[class_]] = class_colors[class_]

    box_table_counter["Sum"] = [len(original_detection_output), len(perturbed_detection_output)]
    return display_table(
        box_table_counter, header=["Original", "Perturbed"], highlight_row_header=highlights
    )


def display_detection_observation(
    observation: PIL.Image.Image,
    observation_inference: List[ImageObjectDetectionBoundingBox],
    class_names: List[str],
    class_colors: List[str],
    class_filter: str = "All Classes",
    title: Optional[str] = None,
    caption: Optional[str] = None,
) -> Union[widgets.VBox, widgets.Image]:
    """
    Create a widget displaying a single observation.

    :param observation: Observation to display.
    :param observation_inference: Inference of the passed observation.
    :param class_names: List of all class names.
    :param class_colors: List of colors in RGB.
    :param class_filter: Class name of the class to display,
                         or "All Classes".
    :param title: Title to display above the observation.
    :param caption: Caption to be displayed below the observation.
    :return: Widget containing the observation.
    """
    org = observation.copy()

    for bbox in observation_inference:
        if class_filter not in ["All Classes", class_names[bbox.class_index]]:
            continue
        new = PIL.Image.new("RGBA", observation.size, (255, 255, 255, 0))
        draw = PIL.ImageDraw.Draw(new)

        x1, y1, x2, y2 = (  # pylint: disable=invalid-name
            bbox.min_x,
            bbox.min_y,
            bbox.max_x,
            bbox.max_y,
        )
        if isinstance(x1, float):

            x1 = int(x1 * observation.size[0])  # pylint: disable=invalid-name
            x2 = int(x2 * observation.size[0])  # pylint: disable=invalid-name
            y1 = int(y1 * observation.size[1])  # pylint: disable=invalid-name
            y2 = int(y2 * observation.size[1])  # pylint: disable=invalid-name

        draw.rectangle(
            ((x1, y1), (x2, y2)),
            fill=(255, 0, 0, 0),
            width=int(observation.size[1] / 100),
            outline=class_colors[bbox.class_index],
        )

        org = PIL.Image.alpha_composite(org.convert("RGBA"), new)

    buff = io.BytesIO()
    org.save(buff, format="png")

    observation_widget = widgets.Image(
        value=buff.getvalue(),
        width=300,
        height=400,
    )

    widget_list = [observation_widget]

    if title:
        title_widget = widgets.HTML(value=title)
        widget_list = [title_widget] + widget_list

    if caption:
        caption_widget = widgets.HTML(value=caption)
        widget_list.append(caption_widget)

    if len(widget_list) == 1:
        return observation_widget

    return widgets.VBox(widget_list)


def display_selection_class_detection_widget(
    observation_image: PIL.Image,
    adversarial_example_image: PIL.Image,
    observation_detection_output: List[ImageObjectDetectionBoundingBox],
    adversarial_example_detection_output: List[ImageObjectDetectionBoundingBox],
    class_names: List[str],
    class_colors: List[str],
    observation_title: Optional[str] = None,
    observation_caption: Optional[str] = None,
    perturbation_title: Optional[str] = None,
    perturbation_caption: Optional[str] = None,
) -> widgets.VBox:
    """
    Create a widget displaying an object detection inference in addition to a
    selector filtering the output by class.

    :param observation_image: Image of the original observation.
    :param adversarial_example_image: Image of the adversarial example.
    :param observation_detection_output: Inference of the original observation.
    :param adversarial_example_detection_output: Inference of the adversarial example.
    :param class_names: List of all class names.
    :param class_colors: List of colors in RGB.
    :param observation_title: Title to be displayed above the original observation.
    :param observation_caption: Caption to be displayed under the original observation.
    :param perturbation_title: Title to be displayed above the perturbed observation.
    :param perturbation_caption: Caption to be displayed under the perturbed observation.
    :return: Widget displaying both detection outputs with a selector to either
             display only boxes of the selected class or to display all boxes.
    """
    class_indices = list(
        set(
            [bbox.class_index for bbox in observation_detection_output]
            + [bbox.class_index for bbox in adversarial_example_detection_output]
        )
    )
    filtered_class_names = [class_names[idx] for idx in class_indices]

    class_selection = widgets.Dropdown(
        options=["All Classes"] + filtered_class_names,
        value="All Classes",
        description="Filter Bounding Boxes:",
        disabled=False,
    )
    class_selection.style.description_width = "150px"

    # Generate the widgets for each class
    detection_observation_widgets_per_class = []
    for class_filter in class_selection.options:
        detection_observation_widgets_per_class.append(
            widgets.HBox(
                [
                    display_detection_observation(
                        observation_image,
                        observation_detection_output,
                        class_names=class_names,
                        class_colors=class_colors,
                        class_filter=class_filter,
                        title=observation_title,
                        caption=observation_caption,
                    ),
                    display_detection_observation(
                        adversarial_example_image,
                        adversarial_example_detection_output,
                        class_names=class_names,
                        class_colors=class_colors,
                        class_filter=class_filter,
                        title=perturbation_title,
                        caption=perturbation_caption,
                    ),
                ]
            )
        )

    detection_observation_widget = widgets.Stack(detection_observation_widgets_per_class)
    widgets.jslink((class_selection, "index"), (detection_observation_widget, "selected_index"))

    return widgets.VBox(children=[detection_observation_widget, class_selection])
