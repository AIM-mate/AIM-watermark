import copy
import tempfile
from importlib import resources

import pypdf

from aim_watermark import images
from aim_watermark.settings import Settings


def get_page_map(
    bookmarkPDF,
    pages=None,
    result=None,
    number_pages=None,
) -> dict:
    # Questa funzione costruisce un dizionario che mette in
    # corrispondenza ricorsivamente il numero della pagina e il suo
    # id (Perchè si debba fare così per i pdf non lo so ma va fatto
    # per potersi poi riferire alla pagina nelle funzioni di pypdf).

    if result is None:
        result = {}
    if pages is None:
        number_pages = []
        pages = bookmarkPDF.trailer["/Root"].get_object()["/Pages"].get_object()
    t = pages["/Type"]
    if t == "/Pages":
        for page in pages["/Kids"]:
            result[page.idnum] = len(number_pages)
            get_page_map(bookmarkPDF, page.get_object(), result, number_pages)
    elif t == "/Page":
        number_pages.append(1)
    return result


def transfer_bookmarks(
    out_pdf,
    outlines,
    page_map=None,
    parent=None,
):
    # Questa funzione scorre le outline del documento ricorsivamente
    # se trova una lista scorre anche quella, in caso contrario se
    # trova un bookmark con genitore glielo assegna, se no lo crea
    # sulla pagina tramite il dizionario usandone l'id come chiave
    # (+1 perchè le pagine partono da 0)
    # La risposta originale estraeva anche '/Top' e '/Left' dall'outline
    # ma ciò è valido se per i bookmark con '/Type'='/XYZ' e inoltre
    # non veniva adoperato dal codice originale, dunque l'ho cancellato.

    for outline in outlines:
        if isinstance(outline, pypdf.generic.Destination):
            outdict = {
                "title": outline["/Title"],
                "page": page_map[outline.page.idnum] + 1,
            }
            if parent:
                _parent = out_pdf.add_outline_item(
                    title=outdict["title"],
                    page_number=outdict["page"] - 1,
                    parent=parent,
                )
            else:
                _parent = out_pdf.add_outline_item(title=outdict["title"], page_number=outdict["page"] - 1)
        elif isinstance(outline, list):
            out_pdf = transfer_bookmarks(out_pdf, outline, page_map, _parent)

    return out_pdf


def copy_bookmarks(
    bookmarks_source_path: str,
    source_file_path: str,
    destination_file_path: str,
) -> None:
    # Questa funzione copia le pagine dal doc modificato a quello nuovo
    # e poi trasferisce i bookmark dall'originale.

    # apro i file con pypdf
    bookmarks_source_pdf = pypdf.PdfReader(bookmarks_source_path)
    source_file_pdf = pypdf.PdfReader(source_file_path)
    destination_file_pdf = pypdf.PdfWriter()

    # trasferisco le pagine dal modificato al nuovo
    for page_number in range(len(source_file_pdf.pages)):
        page = source_file_pdf.pages[page_number]
        destination_file_pdf.add_page(page)

    # trasferisco i bookmark dall'originale al nuovo
    page_map = get_page_map(bookmarks_source_pdf)
    outlines = bookmarks_source_pdf.outline
    destination_file_pdf = transfer_bookmarks(destination_file_pdf, outlines, page_map)

    # salvo il nuovo documento
    destination_file_pdf.write(destination_file_path)


def apply_watermark(
    source_file_path: str,
    destination_file_path: str,
    settings: Settings,
) -> None:
    # Read watermark
    watermark_path = resources.files(images) / "logo-aim.pdf"
    watermark_page = pypdf.PdfReader(watermark_path).pages[0]

    reader = pypdf.PdfReader(source_file_path)
    writer = pypdf.PdfWriter()
    writer.append(reader, pages=list(range(len(reader.pages))))

    for page in writer.pages:
        # Get dimensions of the current page
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)

        # Get dimensions of the watermark
        watermark_width = float(watermark_page.mediabox.width)
        watermark_height = float(watermark_page.mediabox.height)

        # Calculate new dimensions for the watermark
        shorter_side = min(page_width, page_height)
        new_logo_width = shorter_side * settings.scale / 100
        watermark_aspect_ratio = watermark_width / watermark_height
        new_logo_height = new_logo_width / watermark_aspect_ratio
        logo_scaling = new_logo_width / watermark_width

        # Set padding as a percentage of the shorter side
        padding = shorter_side * settings.padding / 100

        # Determine position
        translate_x, translate_y = 0, 0
        if settings.position == "topleft":
            translate_x, translate_y = (
                padding,
                page_height - new_logo_height - padding,
            )
        elif settings.position == "topright":
            translate_x, translate_y = (
                page_width - new_logo_width - padding,
                page_height - new_logo_height - padding,
            )
        elif settings.position == "bottomleft":
            translate_x, translate_y = padding, padding
        elif settings.position == "bottomright":
            translate_x, translate_y = (
                page_width - new_logo_width - padding,
                padding,
            )
        elif settings.position == "center":
            translate_x, translate_y = (
                (page_width - new_logo_width) // 2,
                (page_height - new_logo_height) // 2,
            )

        # merge the page with the transformation
        page.merge_transformed_page(
            watermark_page,
            ctm=[logo_scaling, 0, 0, logo_scaling, translate_x, translate_y],
            over=True,
        )

    with tempfile.NamedTemporaryFile() as tmp:
        writer.write(tmp)
        copy_bookmarks(source_file_path, tmp, destination_file_path)
