import io
import os
import pathlib
from collections.abc import Iterable
from typing import Union
from uuid import uuid4

# from pdf2image import convert_from_bytes
import pdf2image
from pdfminer.high_level import extract_pages
from pdfminer.layout import (
    LTChar,
    LTCurve,
    LTFigure,
    LTImage,
    LTLine,
    LTPage,
    LTRect,
    LTText,
    LTTextBox,
    LTTextLine,
)
from PIL import Image as PILImage
from PIL import ImageChops
from pypdf import PdfReader, PdfWriter

from readyocr.entities import (
    Block,
    BoundingBox,
    Character,
    Document,
    DrawCurve,
    DrawLine,
    DrawRectangle,
    Figure,
    Image,
    Line,
    Page,
)


class PDFData:
    def __init__(self, pdf_content, last_page, load_image, remove_text):
        self.load_image = load_image
        self.remove_text = remove_text

        self.pages = []
        try:
            self.pages = self._parse_pages(pdf_content, last_page)
        except Exception as e:
            print("Fail to use PDFMiner extract text")
            print(e)

        self.images = []
        if load_image:
            try:
                self.images = self._extract_image(pdf_content, last_page)
            except Exception as e:
                print("Fail to use pdf2image")
                print(e)

        self.remove_text_images = []
        if load_image:
            try:
                self.remove_text_images = self._extract_image_remove_text(
                    pdf_content, last_page
                )
            except Exception as e:
                print("Fail to use pypdf")
                print(e)

        self.document = self._gen_document()

        self.clean_page_images = []

    def check_invisible_character(self, page, image, non_text_image):
        # check different image between image and non_text_image
        diff_image = ImageChops.difference(image, non_text_image).convert("L")
        for character in page.descendants.filter_by_class(Character):
            # check if character is invisible
            character.metadata["invisible"] = self._is_invisible(character, diff_image)
            if (
                "font-family" in character.metadata
                and "CIDFont" in character.metadata["font-family"]
            ):
                character.metadata["invisible"] = True

    def _is_invisible(self, character, diff_image):
        # ignore all cid encoded character
        if character.text.startswith("(cid"):
            return True

        if character.text.strip() == "":
            return False

        xmin = int(character.bbox.xmin * diff_image.size[0])
        ymin = int(character.bbox.ymin * diff_image.size[1])
        xmax = int(character.bbox.xmax * diff_image.size[0])
        ymax = int(character.bbox.ymax * diff_image.size[1])

        cropped_diff_image = diff_image.crop((xmin, ymin, xmax, ymax))
        return cropped_diff_image.getbbox() is None

    def get_remove_visible_character(self, page, image, non_text_image):
        new_image = image.copy()
        for character in page.descendants.filter_by_class(Character):
            if character.metadata.get("invisible"):
                continue
            xmin = int(character.bbox.xmin * image.size[0])
            ymin = int(character.bbox.ymin * image.size[1])
            xmax = int(character.bbox.xmax * image.size[0])
            ymax = int(character.bbox.ymax * image.size[1])
            new_image.paste(
                non_text_image.crop((xmin, ymin, xmax, ymax)), (xmin, ymin, xmax, ymax)
            )

        return new_image

    def _gen_document(self):
        document = Document()

        if len(self.images) == len(self.remove_text_images) and len(self.images) == len(
            self.pages
        ):
            for image, non_text_image, page in zip(
                self.images, self.remove_text_images, self.pages
            ):
                self.check_invisible_character(page, image, non_text_image)
                if self.remove_text:
                    image = self.get_remove_visible_character(
                        page, image, non_text_image
                    )
                page.image = image
                page.width = image.size[0]
                page.height = image.size[1]
                document.add(page)

        elif len(self.images) == len(self.pages):
            for image, page in zip(self.images, self.pages):
                page.image = image
                page.width = image.size[0]
                page.height = image.size[1]
                document.add(page)

        elif len(self.pages) > 0:
            for page in self.pages:
                document.add(page)

        else:
            for idx, image in enumerate(self.images):
                page = Page(
                    page_number=idx + 1,
                    width=image.width,
                    height=image.height,
                    image=image,
                )
                page.width = image.size[0]
                page.height = image.size[1]
                document.add(page)

        return document

    def _extract_image(self, pdf_content, last_page):
        images = pdf2image.convert_from_bytes(
            pdf_content, last_page=last_page, fmt="jpeg"
        )
        return [image.convert("RGB") for image in images]

    def _extract_image_remove_text(self, pdf_content, last_page):
        pdf_writer = PdfWriter()
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        pdf_writer.remove_text()

        # Save the modified PDF content to a new BytesIO object
        pdf_output = io.BytesIO()
        pdf_writer.write(pdf_output)
        pdf_output.seek(0)  # Reset the stream position to the beginning
        pdf_content = pdf_output.getvalue()

        images = pdf2image.convert_from_bytes(
            pdf_content, last_page=last_page, fmt="jpeg"
        )
        images = [image.convert("RGB") for image in images]

        return images

    def _parse_pages(self, pdf_content, last_page):
        pages = []
        ltpages = extract_pages(io.BytesIO(pdf_content), maxpages=last_page)

        for ltpage in ltpages:
            page = Page(
                page_number=ltpage.pageid, width=ltpage.width, height=ltpage.height
            )
            
            for item in ltpage:
                page_entity = self._parse_page_entity(item, page)
                if page_entity is not None:
                    page.add(page_entity)

            pages.append(page)

        return pages

    def _parse_bbox(self, item, page):
        x = float(item.x0 / page.width)
        y = float((page.height - item.y1) / page.height)
        width = float(item.width / page.width)
        height = float(item.height / page.height)

        return BoundingBox(
            x=min(1, max(0, x)),
            y=min(1, max(0, y)),
            width=min(1, max(0, width)),
            height=min(1, max(0, height)),
        )

    def _parse_points(self, points, page):
        xmin = min([point[0] for point in points])
        ymin = min([point[1] for point in points])
        xmax = max([point[0] for point in points])
        ymax = max([point[1] for point in points])

        x = float(xmin / page.width)
        y = float((page.height - ymax) / page.height)
        width = float((xmax - xmin) / page.width)
        height = float((ymax - ymin) / page.height)

        return BoundingBox(
            x=min(1, max(0, x)),
            y=min(1, max(0, y)),
            width=min(1, max(0, width)),
            height=min(1, max(0, height)),
        )
    
    def _is_out_of_page(self, item, page):
        x = float(item.x0 / page.width)
        y = float((page.height - item.y1) / page.height)
        width = float(item.width / page.width)
        height = float(item.height / page.height)
        xmin = x
        ymin = y
        xmax = x+width
        ymax = y+height

        if xmin > 1 or xmin < 0:
            return True
        if ymin > 1 or ymin < 0:
            return True
        if xmax > 1 or xmax < 0:
            return True
        if ymax > 1 or ymax < 0:
            return True
        
        return False

    def _parse_page_entity(self, item, page):
        obj = None

        if isinstance(item, LTLine):
            obj = DrawLine(
                id=str(uuid4()), bbox=self._parse_points(item.pts, page), confidence=1
            )
        elif isinstance(item, LTRect):
            obj = DrawRectangle(
                id=str(uuid4()), bbox=self._parse_points(item.pts, page), confidence=1
            )
        elif isinstance(item, LTCurve):
            obj = DrawCurve(
                id=str(uuid4()), bbox=self._parse_points(item.pts, page), confidence=1
            )
        elif isinstance(item, LTFigure):
            obj = Figure(
                id=str(uuid4()), bbox=self._parse_bbox(item, page), confidence=1
            )
        elif isinstance(item, LTImage):
            obj = Image(
                id=str(uuid4()), bbox=self._parse_bbox(item, page), confidence=1
            )
        elif isinstance(item, LTTextLine):
            if "(cid:" in item.get_text():
                return None
            
            if self._is_out_of_page(item, page):
                return None
            obj = Line(
                id=str(uuid4()),
                bbox=self._parse_bbox(item, page),
                text=item.get_text(),
                confidence=1,
            )
        elif isinstance(item, LTTextBox):
            if "(cid:" in item.get_text():
                return None
            
            if self._is_out_of_page(item, page):
                return None
            obj = Block(
                id=str(uuid4()),
                bbox=self._parse_bbox(item, page),
                text=item.get_text(),
                confidence=1,
            )
        elif isinstance(item, LTChar):
            if "(cid:" in item.get_text():
                return None
            
            if self._is_out_of_page(item, page):
                return None
            
            obj = Character(
                id=str(uuid4()),
                bbox=self._parse_bbox(item, page),
                text=item.get_text(),
                confidence=1,
                metadata={
                    # "line-width": item.graphicstate.linewidth,
                    # "line-cap": item.graphicstate.linecap,
                    # "line-join": item.graphicstate.linejoin,
                    # "miter-limit": item.graphicstate.miterlimit,
                    # "dash": item.graphicstate.dash,
                    # "intent": item.graphicstate.intent,
                    # "flatness": item.graphicstate.flatness,
                    "color-space": item.ncs.name,
                    "ncomponents": item.ncs.ncomponents,
                    "font-family": item.fontname,
                    "font-size": item.size,
                    "text-stroke-color": item.graphicstate.scolor,
                    "text-fill-color": item.graphicstate.ncolor,
                },
            )
        elif isinstance(item, LTText):
            pass
        else:
            assert False, str(("Unhandled", item))

        if isinstance(item, Iterable):
            for child in item:
                child_obj = self._parse_page_entity(child, page)
                if child_obj is not None:
                    obj.add(child_obj)

        return obj


def load(
    pdf_file: Union[pathlib.PurePath, str, bytes],
    last_page: int = None,
    load_image=True,
    remove_text=True,
) -> Document:
    """
    Load a PDF file into a Document object.

    :param pdf_file: Either a file path or a bytes object for the PDF file to be worked on.
    :type pdf_file: Union[pathlib.PurePath, str, bytes]
    :param last_page: The last page to be loaded, defaults to None
    :type last_page: int, optional
    :param load_image: if the image is loaded, defaults to False
    :type load_image: bool, optional
    :param remove_text: if the text is removed, defaults to False
    :type remove_text: bool, optional
    :return: A Document object
    :rtype: Document
    """
    if isinstance(pdf_file, pathlib.PurePath):
        pdf_file = str(pdf_file)

    if isinstance(pdf_file, str):
        with open(pdf_file, "rb") as fp:
            pdf_content = fp.read()
    elif isinstance(pdf_file, bytes):
        pdf_content = pdf_file
    else:
        raise TypeError("pdf_file must be a file path or a file-like object.")

    pdf_data = PDFData(pdf_content, last_page, load_image, remove_text)

    document = pdf_data.document

    return document
