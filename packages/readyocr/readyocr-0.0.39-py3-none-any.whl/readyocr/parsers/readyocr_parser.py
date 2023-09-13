from typing import Dict

from readyocr.entities import (
    Block,
    BoundingBox,
    Cell,
    Character,
    Document,
    EntityList,
    Field,
    Figure,
    Image,
    Invoice,
    Key,
    Line,
    LineItem,
    LineItemGroup,
    MergedCell,
    Page,
    Paragraph,
    Table,
    Value,
    Word,
)


def _create_object(entity_json):
    """_summary_

    :param entity_json: entity information json format
    :type entity_json: json
    """
    if "boundingBox" in entity_json:
        bbox = BoundingBox(
            entity_json["boundingBox"]["x"],
            entity_json["boundingBox"]["y"],
            entity_json["boundingBox"]["width"],
            entity_json["boundingBox"]["height"],
        )
    else:
        bbox = None
        
    if entity_json["class"] == "Table":
        entity = Table(id=entity_json["id"], bbox=bbox, confidence=1.0)
    elif entity_json["class"] == "Cell":
        entity = Cell(
            id=entity_json["id"],
            bbox=bbox,
            row_index=entity_json.get("rowIndex"),
            col_index=entity_json.get("columnIndex"),
            text=entity_json.get("text"),
            confidence=entity_json.get("confidence"),
        )
    elif entity_json["class"] == "MergedCell":
        entity = MergedCell(
            id=entity_json["id"],
            bbox=bbox,
            row_index=entity_json.get("rowIndex"),
            col_index=entity_json.get("columnIndex"),
            row_span=entity_json["rowSpan"],
            col_span=entity_json["columnSpan"],
            text=entity_json.get("text"),
            confidence=entity_json.get("confidence"),
        )
    elif entity_json["class"] in (
        "Word",
        "Line",
        "Key",
        "Value",
        "Character",
        "Paragraph",
        "Block",
    ):
        entity = eval(entity_json["class"])(
            id=entity_json["id"],
            bbox=bbox,
            text=entity_json.get("text"),
            confidence=entity_json.get("confidence"),
        )
    elif entity_json["class"] in ("Image", "Figure"):
        entity = eval(entity_json["class"])(
            id=entity_json["id"], 
            bbox=bbox, 
            confidence=entity_json.get("confidence")
        )
    elif entity_json["class"] == "Field":
        entity = Field(
            id=entity_json["id"],
            bbox=bbox,
            text=entity_json.get("text"),
            confidence=entity_json.get("confidence"),
            type=entity_json.get("type"),
            page_number=entity_json.get("pageNumber"),
        )
    else:
        entity = None
    return entity


def _parse_invoice(invoice_json):
    page_numbers = invoice_json.get("pageNumbers")
    fields_json = invoice_json.get("fields")
    line_item_groups_json = invoice_json.get("lineItemGroups")

    fields = []
    for field_json in fields_json:
        field = _create_object(field_json)
        fields.append(field)

    line_item_groups = []
    for line_item_group_json in line_item_groups_json:
        line_item_group = []
        for line_item_json in line_item_group_json.get("LineItems"):
            for item_json in line_item_json:
                item = _create_object(item_json)
                line_item_group.append(item)
        line_item_groups.append(line_item_group)

    return Invoice(
        fields=fields,
        line_item_groups=line_item_groups,
        page_numbers=page_numbers,
    )


def load(response: Dict) -> Document:
    """
    Convert ReadyOCR json to ReadyOCR document

    :param response: json response from readyocr
    :type response: Dict
    :return: ReadyOCR document
    :rtype: Document
    """
    document = Document()
    for page_json in response["document"]["pages"]:
        # initialize page object
        page = Page(
            page_number=page_json["pageNumber"],
            width=page_json["dimension"]["width"],
            height=page_json["dimension"]["height"],
        )
        # add entity into page
        for entity_json in page_json["entities"]:
            entity = _create_object(entity_json=entity_json)
            if entity is not None:
                page.add(entity)
        # linking entities
        for entity_json in page_json["entities"]:
            parent_entities = page.children.filter_by_attr("id", entity_json["id"])
            if len(parent_entities) > 0:
                parent_entity = parent_entities[0]
                if entity_json.get("childrenIds"):
                    for child_id in entity_json.get("childrenIds"):
                        child_entity = page.children.filter_by_attr("id", child_id)
                        if len(child_entity) > 0:
                            parent_entity.add(child_entity[0])
        # add more things into page
        document.add(page)

    invoices_json = response.get("document").get("invoices")
    if invoices_json is not None:
        for invoice_json in invoices_json:
            invoice = _parse_invoice(invoice_json)

            document.invoices.append(invoice)

    return document
