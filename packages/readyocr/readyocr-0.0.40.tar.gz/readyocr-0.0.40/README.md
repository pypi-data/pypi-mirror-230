[![License: MIT](https://img.shields.io/github/license/syanng/readyocr)](https://opensource.org/licenses/MIT) [![PyPI Version](https://img.shields.io/pypi/v/readyocr)](https://pypi.org/project/readyocr/) [![Downloads](https://img.shields.io/pypi/dm/readyocr)](https://pypi.org/project/readyocr/)


# ReadyOCR

ReadyOCR is a Python library that allows you to quickly and easily parse data from various OCR API services, including AWS Textract and Google Document AI. The package also comes with nice features for searching and visualizing.

![Textract Output Visualize](https://raw.githubusercontent.com/syanng/readyocr/main/images/visualize.png)

## Installation

You can install ReadyOCR using pip. Depending on the OCR API service you want to use, you can install the corresponding version of ReadyOCR:

* For minimal usage, if you only want to create ReadyOCR document object format:

    ```
    pip install readyocr
    ```

* Or you can choose a specific version to support a specific API response:

    ```
    # support AWS Textract response
    pip install "readyocr[textract]"

    # support Google Document AI response
    pip install "readyocr[documentai]"

    # support all available
    pip install "readyocr[all]"
    ```

## Basic Usage

* ReadyOCR allows you to create a Document object, which represents the OCR results. A Document can contain one or many pages, and each page can have multiple page entity objects, such as line, word, or table.

    ```
    from readyocr.entities import Document, Page, Block, Paragraph, Line, Word, Table, Cell, Key, Value

    document = Document(...)
    page = Page(...)
    word = Word(...)

    # linking all object
    page.add(word)
    document.pages.append(page)
    ```

* You can define any document structure you want by using the `.children` property for page entities. For example, a line object can have many word objects as children.

    ```
    page = Page(...)
    line = Line(...)
    word1 = Word(...)
    word2 = Word(...)

    line.children = [word1, word2]

    # add line object to page children
    page.add(line)

    # you can get descendant of a object
    all_page_entity = page.descendant

    # you can also filter all object by class, tag or attribute
    all_word = page.descendant.filter_by_class(Word)
    ```

* ReadyOCR allows you to read PDF file with page object Line, Character, Figure, and Image. You can read from both path and byte stream
    ```
    from readyocr.parsers.pdf_parser import load
    
    document = load(pdf_path, load_image=True, remove_text=False)
    ...
    with open(pdf_path, 'rb') as fp:
        byte_obj = fp.read()
        document = load(byte_obj, load_image=True, remove_text=False)
    ```

* You can also use tags attribute to identify some specific attribute:

    ```
    table = Table(...)
    cell = Cell(...)
    cell.tags.add('COLUMN_HEADER')
    table.add(cell)

    # Get all table cell which is column header
    table.children.filter_by_tags('COLUMN_HEADER') 
    ```

* ReadyOCR support export json object and also load from same json object

    ```
    from readyocr.parsers.readyocr_parser import load

    ...
    # python object -> python dict
    dict_resp = document.export_json()

    # python dict -> python object
    same_document = load(dict_resp)
    ```

* ReadyOCR support visualize for bounding box and textbox

    ```
    from readyocr.utils.visualize import draw_bbox, draw_textbox
    
    bbox_image = page.image.copy()
    text_image = page.image.copy()

    for item in page.descendants.filter_by_class(Line):
        bbox_image = draw_bbox(
            image=bbox_image,
            bbox=item,
            fill_color=(0, 255, 0),
            outline_color=(0, 255, 0), 
            opacity=0.2
        )
        text_image = draw_textbox(
            image=text_image, 
            textbox=item,
            padding=1,
            true_font_path="../fonts/arial.ttf",
        )
    ```

    ![Textract Textbox Output Visualize](https://raw.githubusercontent.com/syanng/readyocr/main/images/visualize_textbox.png)

### Examples

Please find all the available [examples](examples/) for better understanding ReadyOCR.

### License

ReadyOCR is released under the MIT license. See the [LICENSE](LICENSE) file for more details.
