import os
from typing import List

from PIL import Image, ImageDraw, ImageFont

from readyocr.entities import BoundingBox, EntityList, PageEntity, TextBox

present_path = os.path.abspath(os.path.dirname(__file__))


def draw_bboxes(
    images: List[Image.Image],
    bboxes: List[BoundingBox],
    fill_color: tuple = (0, 0, 255),
    outline_color: tuple = (0, 255, 0),
    outline_thickness: int = 1,
    opacity: float = 0.3,
) -> Image.Image:
    """
    Draws boxes on the images with the specified parameters.

    :param images: The input images.
    :type images: list
    :param bboxes: The bounding box coordinates (x, y, width, height - normalized).
    :type bboxes: list
    :param fill_color: The color of the box, defaults to [0, 0, 255] (blue).
    :type fill_color: list, optional
    :param outline_color: The color of the outline, defaults to [0, 255, 0] (green).
    :type outline_color: list, optional
    :param outline_thickness: The thickness of the outline, defaults to 1.
    :type outline_thickness: int, optional
    :param opacity: The opacity of the box, defaults to 0.5.
    :type opacity: float, optional
    :return: The image with the drawn boxes.
    :rtype: Image
    """
    for image, bbox in zip(images, bboxes):
        image = draw_bbox(
            image, bbox, fill_color, outline_color, outline_thickness, opacity
        )

    return image


def draw_textboxes(
    images: List[Image.Image],
    textboxes: List[TextBox],
    text_color: tuple = (0, 0, 0),
    background_color: tuple = (255, 255, 255),
    outline_color: tuple = (0, 255, 0),
    outline_thickness: int = 1,
    padding: int = 5,
    true_font_path: str = None,
) -> Image.Image:
    """
    Draws textboxes on the images with the specified parameters.

    :param images: The input images.
    :type images: list
    :param textboxes: The textboxes to draw.
    :type textboxes: list
    :param text_color: The color of the text, defaults to [0, 0, 0] (black).
    :type text_color: list, optional
    :param background_color: The color of the background, defaults to [255, 255, 255] (white).
    :type background_color: list, optional
    :param opacity: The opacity of the background, defaults to 1.
    :type opacity: float, optional
    :return: The image with the drawn textboxes.
    :rtype: Image
    """
    for image, textbox in zip(images, textboxes):
        image = draw_textbox(
            image,
            textbox,
            text_color,
            background_color,
            outline_color,
            outline_thickness,
            padding,
            true_font_path,
        )

    return image


def draw_bbox(
    image: Image.Image,
    bbox: BoundingBox,
    fill_color: tuple = (0, 0, 255),
    outline_color: tuple = (0, 255, 0),
    outline_thickness: int = 1,
    opacity: float = 0.3,
) -> Image:
    """
    Draws a box on the image with the specified parameters.

    :param image: The input image.
    :type image: Image
    :param bbox: The bounding box coordinates (x, y, width, height - normalized).
    :type bbox: BoundingBox
    :param fill_color: The color of the box, defaults to [0, 0, 255] (blue).
    :type fill_color: list, optional
    :param outline_color: The color of the outline, defaults to [0, 255, 0] (green).
    :type outline_color: list, optional
    :param outline_thickness: The thickness of the outline, defaults to 1.
    :type outline_thickness: int, optional
    :param opacity: The opacity of the box, defaults to 0.5.
    :type opacity: float, optional
    :return: The image with the drawn box.
    :rtype: Image
    """
    image = image.convert("RGBA")
    x, y, width, height = bbox.x, bbox.y, bbox.width, bbox.height
    left = int(x * image.width)
    top = int(y * image.height)
    right = int((x + width) * image.width)
    bottom = int((y + height) * image.height)

    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    drw = ImageDraw.Draw(overlay, "RGBA")

    # Draw the box
    drw.rectangle(
        [(left, top), (right, bottom)],
        fill=(*fill_color, int(255 * opacity)),
        outline=(*outline_color, 255),
        width=outline_thickness,
    )

    # Combine the overlay with the original image
    image = Image.alpha_composite(image, overlay)

    return image


def draw_textbox(
    image: Image.Image,
    textbox: TextBox,
    custom_text: str = None,
    text_color: tuple = (0, 0, 0),
    background_color: tuple = (255, 255, 255),
    outline_color: tuple = (0, 255, 0),
    outline_thickness: int = 1,
    padding: int = 5,
    true_font_path: str = None,
    font_size: int = None,
):
    """
    Draws a textbox on the image with the specified parameters.

    :param image: The input image.
    :type image: Image
    :param textbox: The textbox to draw.
    :type textbox: TextBox
    :param custom_text: The text to draw, defaults to None.
    :type custom_text: str, optional
    :param text_color: The color of the text, defaults to [0, 0, 0] (black).
    :type text_color: list, optional
    :param background_color: The color of the background, defaults to [255, 255, 255] (white).
    :type background_color: list, optional
    :param outline_color: The color of the outline, defaults to [0, 255, 0] (green).
    :type outline_color: list, optional
    :param outline_thickness: The thickness of the outline, defaults to 1.
    :type outline_thickness: int, optional
    :param padding: The padding of the text, defaults to 5.
    :type padding: int, optional
    :param true_font_path: The path to the true font, defaults to None.
    :type true_font_path: str, optional
    :param font_size: The size of the font, defaults to 12.
    :type font_size: int, optional
    :return: The image with the drawn textbox.
    :rtype: Image
    """
    image = image.convert("RGBA")
    x, y, width, height = (
        textbox.bbox.x,
        textbox.bbox.y,
        textbox.bbox.width,
        textbox.bbox.height,
    )
    left = int(x * image.width)
    top = int(y * image.height)
    right = int((x + width) * image.width)
    bottom = int((y + height) * image.height)
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    drw = ImageDraw.Draw(overlay, "RGBA")

    text = custom_text if custom_text else textbox.text

    if font_size is None:
        # Create a loop to dynamically adjust the font size
        font = ImageFont.load_default()
        if true_font_path is not None:
            font_size = 2
            position = (left, top)
            while True:
                font = ImageFont.truetype(true_font_path, font_size)
                left, top, right, bottom = drw.textbbox(position, text, font=font)
                text_height = bottom - top
                text_width = right - left

                if (
                    text_height >= textbox.height * image.height
                    or text_width >= textbox.width * image.width
                ):
                    font_size -= 1
                    break  # Break the loop if the text fits within the desired height

                font_size += 1  # Decrease the font size if the text is too tall
    else:
        font = ImageFont.load_default()
        if true_font_path is not None:
            font = ImageFont.truetype(true_font_path, font_size)

    drw.rectangle(
        (left - padding, top - padding, right + padding, bottom + padding),
        fill=background_color,
        outline=(*outline_color, 255),
        width=outline_thickness,
    )
    drw.text((left, top), text, font=font, fill=text_color)

    # Combine the overlay with the original image
    image = Image.alpha_composite(image, overlay)

    return image
