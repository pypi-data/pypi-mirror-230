import json
from typing import Dict
from uuid import uuid4

from google.cloud import documentai_v1 as documentai

from readyocr.entities import (Block, BoundingBox, Cell, Document, Key, Line,
                               Page, Paragraph, Table, Value, Word)


def _parse_text(text: str, text_anchor: dict):
    return " ".join(
        [
            text[text_segment.start_index : text_segment.end_index]
            for text_segment in text_anchor.text_segments
        ]
    )


def _parse_bbox(bounding_poly: dict):
    xmin = min([vertex.x for vertex in bounding_poly.normalized_vertices])
    ymin = min([vertex.y for vertex in bounding_poly.normalized_vertices])
    xmax = max([vertex.x for vertex in bounding_poly.normalized_vertices])
    ymax = max([vertex.y for vertex in bounding_poly.normalized_vertices])
    width = xmax - xmin
    height = ymax - ymin

    bbox = BoundingBox(x=xmin, y=ymin, width=width, height=height)

    return bbox


def load(response: Dict) -> Document:
    """
    Convert textract json to readyocr document

    :param response: json response from textract
    :type response: Dict
    :return: readyocr document
    :rtype: Document
    """

    g_document = documentai.Document.from_json(
        json.dumps(response), ignore_unknown_fields=True
    )
    g_text = g_document.text
    document = Document()

    for idx, g_page in enumerate(g_document.pages):
        page = Page(
            page_number=(idx + 1),
            width=g_page.dimension.width,
            height=g_page.dimension.height,
        )
        page.raw_object = g_page

        # Add block to page
        for g_block in g_page.blocks:
            block = Block(
                id=str(uuid4()),
                bbox=_parse_bbox(g_block.layout.bounding_poly),
                text=_parse_text(g_text, g_block.layout.text_anchor),
                confidence=g_block.layout.confidence,
            )
            block.raw_object = g_block
            page.add(block)

        # Add paragraph to page
        for g_paragraph in g_page.paragraphs:
            paragraph = Paragraph(
                id=str(uuid4()),
                bbox=_parse_bbox(g_paragraph.layout.bounding_poly),
                text=_parse_text(g_text, g_paragraph.layout.text_anchor),
                confidence=g_paragraph.layout.confidence,
            )
            paragraph.raw_object = g_paragraph
            page.add(paragraph)

        # Add line to page
        for g_line in g_page.lines:
            line = Line(
                id=str(uuid4()),
                bbox=_parse_bbox(g_line.layout.bounding_poly),
                text=_parse_text(g_text, g_line.layout.text_anchor),
                confidence=g_line.layout.confidence,
            )
            line.raw_object = g_line
            page.add(line)

        # Add word to page
        for g_token in g_page.tokens:
            word = Word(
                id=str(uuid4()),
                bbox=_parse_bbox(g_token.layout.bounding_poly),
                text=_parse_text(g_text, g_token.layout.text_anchor),
                confidence=g_token.layout.confidence,
            )
            word.raw_object = g_token
            page.add(word)

        # Add table and cell to page
        for g_table in g_page.tables:
            table = Table(
                id=str(uuid4()),
                bbox=_parse_bbox(g_table.layout.bounding_poly),
                confidence=g_table.layout.confidence,
            )
            table.raw_object = g_table
            page.add(table)

            row_index = 0
            for g_header_row in g_table.header_rows:
                for col_index, g_cell in enumerate(g_header_row.cells):
                    cell = Cell(
                        id=str(uuid4()),
                        bbox=_parse_bbox(g_cell.layout.bounding_poly),
                        row_index=row_index,
                        col_index=col_index,
                        text=_parse_text(g_text, g_cell.layout.text_anchor),
                        confidence=g_cell.layout.confidence,
                    )
                    cell.raw_object = g_cell
                    cell.tags.add("COLUMN_HEADER")
                    table.add(cell)
                row_index += 1

            for g_body_row in g_table.body_rows:
                for col_index, g_cell in enumerate(g_body_row.cells):
                    cell = Cell(
                        id=str(uuid4()),
                        bbox=_parse_bbox(g_cell.layout.bounding_poly),
                        row_index=row_index,
                        col_index=col_index,
                        text=_parse_text(g_text, g_cell.layout.text_anchor),
                        confidence=g_cell.layout.confidence,
                    )
                    cell.raw_object = g_cell
                    table.add(cell)
                row_index += 1

        # Add key and value to page
        for g_form_field in g_page.form_fields:
            key = Key(
                id=str(uuid4()),
                bbox=_parse_bbox(g_form_field.field_name.bounding_poly),
                text=g_form_field.field_name.text_anchor.content,
                confidence=g_form_field.field_name.confidence,
            )
            key.raw_object = g_form_field.field_name
            page.add(key)

            value = Value(
                id=str(uuid4()),
                bbox=_parse_bbox(g_form_field.field_value.bounding_poly),
                text=g_form_field.field_value.text_anchor.content,
                confidence=g_form_field.field_value.confidence,
            )
            value.raw_object = g_form_field.field_value
            page.add(value)

        document.pages.append(page)

    return document
