import os
from typing import Dict
from uuid import uuid4

from textractor.entities.document import Document as TDocument
from textractor.parsers.response_parser import (
    parse, parser_analyze_expense_response)

from readyocr.entities import (BoundingBox, Cell, Document, Field, Invoice,
                               Key, Line, LineItem, LineItemGroup, MergedCell,
                               Page, Table, Value, Word)


def load_expense(response: Dict) -> Document:
    # parser_analyze_expense_response would be error if Value is empty and don't have boundary
    t_doc = parser_analyze_expense_response(response)
    document = _parse_textract_document(t_doc)

    for expense in t_doc.expense_documents:
        invoice = _parse_expense_document(expense)
        document.invoices.append(invoice)

    return document


def load(response: Dict) -> Document:
    """
    Convert textract json to readyocr document

    :param response: json response from textract
    :type response: Dict
    :return: readyocr document
    :rtype: Document
    """
    t_doc = parse(response)
    document = _parse_textract_document(t_doc)

    return document


def _parse_expense_document(expense_document) -> Invoice:
    fields = []
    for t_field in expense_document.summary_fields_list:
        if t_field.value:
            field = _parse_expense_field(t_field)
            fields.append(field)

    page_numbers = [x.page_number for x in fields]

    line_item_groups = []
    for t_line_item_group in expense_document.line_items_groups:
        line_item_group = []
        for t_line_item in t_line_item_group.rows:
            line_item = []
            for t_item in t_line_item:
                page_numbers.append(t_item.page)
                field = _parse_expense_field(t_item)
                line_item.append(field)
            line_item_group.append(LineItem(line_item))
        line_item_groups.append(LineItemGroup(line_item_group))

    page_numbers = list(set(page_numbers))
    page_numbers.sort()

    return Invoice(
        fields=fields,
        line_item_groups=line_item_groups,
        page_numbers=page_numbers,
    )


def _parse_expense_field(t_field) -> Field:
    field = Field(
        id=str(uuid4()),
        bbox=BoundingBox(
            x=t_field.value.x,
            y=t_field.value.y,
            width=t_field.value.width,
            height=t_field.value.height,
        ),
        type=t_field.type.text,
        text=t_field.value.text,
        confidence=t_field.type.confidence,
        page_number=t_field.page,
    )

    return field


def _parse_textract_document(tdocument: TDocument) -> Document:
    document = Document()

    for t_page in tdocument.pages:
        page = Page(
            page_number=t_page.page_num,
            width=None,
            height=None,
        )

        # Extract t_line t_word from textract and add to readyocr page
        for t_line in t_page.lines:
            line = Line(
                id=t_line.id,
                bbox=BoundingBox(
                    x=t_line.x,
                    y=t_line.y,
                    width=t_line.width,
                    height=t_line.height,
                ),
                text=t_line.text,
                confidence=t_line.confidence,
            )
            page.add(line)

            for t_word in t_line.words:
                word = Word(
                    id=t_word.id,
                    bbox=BoundingBox(
                        x=t_word.x,
                        y=t_word.y,
                        width=t_word.width,
                        height=t_word.height,
                    ),
                    text=t_word.text,
                    confidence=t_word.confidence,
                )
                line.add(word)

        # Extract t_key t_value from textract and add to readyocr page
        for t_key in t_page.key_values:
            t_value = t_key.value

            key = Key(
                id=t_key.id,
                bbox=BoundingBox(
                    x=t_key.x,
                    y=t_key.y,
                    width=t_key.width,
                    height=t_key.height,
                ),
                text="key",
                confidence=t_key.confidence,
            )

            # add word to key
            for t_word in t_key.words:
                word = Word(
                    id=t_word.id,
                    bbox=BoundingBox(
                        x=t_word.x,
                        y=t_word.y,
                        width=t_word.width,
                        height=t_word.height,
                    ),
                    text=t_word.text,
                    confidence=t_word.confidence,
                )

                key.add(word)

            value = Value(
                id=t_value.id,
                bbox=BoundingBox(
                    x=t_value.x,
                    y=t_value.y,
                    width=t_value.width,
                    height=t_value.height,
                ),
                text="value",
                confidence=t_value.confidence,
            )

            # add word to value
            for t_word in t_value.words:
                word = Word(
                    id=t_word.id,
                    bbox=BoundingBox(
                        x=t_word.x,
                        y=t_word.y,
                        width=t_word.width,
                        height=t_word.height,
                    ),
                    text=t_word.text,
                    confidence=t_word.confidence,
                )
                value.add(word)

            key.add(value)
            page.add(key)

        # Extract t_table, t_cell from textract and add to readyocr page
        for t_table in t_page.tables:
            table = Table(
                id=t_table.id,
                bbox=BoundingBox(
                    x=t_table.x,
                    y=t_table.y,
                    width=t_table.width,
                    height=t_table.height,
                ),
                confidence=1,
            )

            # Add all normal table cell
            for t_cell in t_table.table_cells:
                cell = Cell(
                    id=t_cell.id,
                    bbox=BoundingBox(
                        x=t_cell.x,
                        y=t_cell.y,
                        width=t_cell.width,
                        height=t_cell.height,
                    ),
                    row_index=t_cell.row_index,
                    col_index=t_cell.col_index,
                    text=t_cell.text,
                    confidence=t_cell.confidence,
                )

                if t_cell.is_column_header:
                    cell.tags.add("COLUMN_HEADER")
                if t_cell.is_title:
                    cell.tags.add("TITLE")
                if t_cell.is_footer:
                    cell.tags.add("FOOTER")
                if t_cell.is_summary:
                    cell.tags.add("SUMMARY")
                if t_cell.is_section_title:
                    cell.tags.add("SECTION_TITLE")

                for t_word in t_cell.words:
                    word = Word(
                        id=t_word.id,
                        bbox=BoundingBox(
                            x=t_word.x,
                            y=t_word.y,
                            width=t_word.width,
                            height=t_word.height,
                        ),
                        text=t_word.text,
                        confidence=t_word.confidence,
                    )

                    cell.add(word)

                table.add(cell)

            page.add(table)

            # Add all merged table cell
            for t_cell in t_table.table_cells:
                if (
                    len(t_cell.siblings) > 0
                    and len(table.children.filter_by_attr("id", t_cell.parent_cell_id))
                    > 0
                ):
                    x = min([x.x for x in t_cell.siblings])
                    y = min([x.y for x in t_cell.siblings])
                    width = max([x.x + x.width for x in t_cell.siblings]) - x
                    height = max([x.y + x.height for x in t_cell.siblings]) - y
                    row_index = min([x.row_index for x in t_cell.siblings])
                    col_index = min([x.col_index for x in t_cell.siblings])
                    row_span = (
                        max([x.row_index for x in t_cell.siblings])
                        - min([x.row_index for x in t_cell.siblings])
                        + 1
                    )
                    col_span = (
                        max([x.col_index for x in t_cell.siblings])
                        - min([x.col_index for x in t_cell.siblings])
                        + 1
                    )

                    merged_cell = MergedCell(
                        id=t_cell.parent_cell_id,
                        bbox=BoundingBox(
                            x=x,
                            y=y,
                            width=width,
                            height=height,
                        ),
                        row_index=row_index,
                        col_index=col_index,
                        row_span=row_span,
                        col_span=col_span,
                        text="",
                        confidence=1,
                    )

                    for x in table.children:
                        if x.id in [x.id for x in t_cell.siblings]:
                            merged_cell.add(x)

                    table.add(merged_cell)

        document.pages.append(page)

    return document
