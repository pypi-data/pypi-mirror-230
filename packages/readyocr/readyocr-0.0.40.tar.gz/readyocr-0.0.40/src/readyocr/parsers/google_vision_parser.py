from typing import Dict
from uuid import uuid4

from readyocr.entities import BoundingBox, Character, Document, Page, Word


def _create_boundingbox(boundingBox, image_width, image_height):
    xmin, ymin, xmax, ymax = float("inf"), float("inf"), 0, 0
    for vertice in boundingBox["vertices"]:
        x = vertice.get("x")
        y = vertice.get("y")
        if x is not None:
            xmin = min(xmin, x)
            xmax = max(xmax, x)
        if y is not None:
            ymin = min(ymin, y)
            ymax = max(ymax, y)
    x = max(min(xmin / image_width, 1), 0)
    y = max(min(ymin / image_height, 1), 0)
    width = min(max((xmax - xmin) / image_width, 0), 1)
    height = min(max((ymax - ymin) / image_height, 0), 1)

    return BoundingBox(x=x, y=y, width=width, height=height)


def _create_object_word(word, image_height, image_width):
    """_summary_

    :param entity_json: entity information json format
    :type entity_json: json
    """
    # TODO: code to return Page Entity
    text = chars2word(word)
    confidence = word.get("confidence", 0)
    word = Word(
        id=str(uuid4()),
        bbox=_create_boundingbox(word["boundingBox"], image_width, image_height),
        text=text,
        confidence=confidence,
    )

    return word


def _create_object_character(char, image_height, image_width):
    """_summary_

    :param entity_json: entity information json format
    :type entity_json: json
    """
    # TODO: code to return Page Entity
    confidence = char.get("confidence", 0)
    char = Character(
        id=str(uuid4()),
        bbox=_create_boundingbox(char["boundingBox"], image_width, image_height),
        text=char["text"],
        confidence=confidence,
    )
    return char


def chars2word(word):
    text = ""
    for char in word["symbols"]:
        text += char["text"]
    return text


def load(response: Dict) -> Document:
    """Convert GoogleVision OCR json to ReadyOCR document

    :param response: JSON respone from Google Vision
    :type response: Dict
    :return: Readyocr Document
    :rtype: Document
    """
    document = Document()

    full_text = response.get("fullTextAnnotation")
    if full_text == None:
        return document

    for idx, page_gg in enumerate(full_text["pages"]):
        image_height, image_width = page_gg.get("height"), page_gg.get("width")
        page = Page(width=image_width, height=image_height, page_number=idx + 1)
        image_width, image_height = page.width, page.height
        for block in page_gg["blocks"]:
            for paragraph in block["paragraphs"]:
                for word in paragraph["words"]:
                    word_obj = _create_object_word(
                        word, image_height=image_height, image_width=image_width
                    )
                    for char in word["symbols"]:
                        char_obj = _create_object_character(
                            char, image_height, image_width
                        )
                        char_obj.raw_object = char
                        word_obj.add(char_obj)
                    word_obj.raw_object = word
                    page.add(word_obj)
        document.add(page=page)

    return document
