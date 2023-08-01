import os
from pathlib import Path

import pdfrw
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import Destination

from src import constants

# ----- Stack overflow -----
# Presa da questa risposta: https://stackoverflow.com/a/68853751/13373369
# region


class Watermarker:
    def __init__(self, path, overwrite=False):
        self.path = path
        self.overwrite = overwrite
        self.outputpath = ""

        # if self.path doesn't exist, raise an error
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"{self.path} non esiste")

        # if self.path isn't a file, raise an error
        if os.path.isfile(self.path):
            raise FileNotFoundError(f"{self.path} non è un file")

    def get_page_map(self, bookmarkPDF, pages=None, result=None, number_pages=None):
        # Questa funzione costruisce un dizionario che mette in
        # corrispondenza ricorsivamente il numero della pagina e il suo
        # id (Perchè si debba fare così per i pdf non lo so ma va fatto
        # per potersi poi riferire alla pagina nelle funzioni di PyPDF2).

        if result is None:
            result = {}
        if pages is None:
            number_pages = []
            pages = bookmarkPDF.trailer["/Root"].get_object()["/Pages"].get_object()
        t = pages["/Type"]
        if t == "/Pages":
            for page in pages["/Kids"]:
                result[page.idnum] = len(number_pages)
                self.get_page_map(bookmarkPDF, page.get_object(), result, number_pages)
        elif t == "/Page":
            number_pages.append(1)
        return result

    def transfer_bookmarks(self, out_pdf, outlines, page_map=None, parent=None):
        # Questa funzione scorre le outline del documento ricorsivamente
        # se trova una lista scorre anche quella, in caso contrario se
        # trova un bookmark con genitore glielo assegna, se no lo crea
        # sulla pagina tramite il dizionario usandone l'id come chiave
        # (+1 perchè le pagine partono da 0)
        # La risposta originale estraeva anche '/Top' e '/Left' dall'outline
        # ma ciò è valido se per i bookmark con '/Type'='/XYZ' e inoltre
        # non veniva adoperato dal codice originale, dunque l'ho cancellato.

        for outline in outlines:
            if isinstance(outline, Destination):
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
                    _parent = out_pdf.add_outline_item(
                        title=outdict["title"], page_number=outdict["page"] - 1
                    )
            elif isinstance(outline, list):
                out_pdf = self.transfer_bookmarks(out_pdf, outline, page_map, _parent)

        return out_pdf

    def copy_bookmarks(self, original, copy, output):
        # Questa funzione copia le pagine dal doc modificato a quello nuovo
        # e poi trasferisce i bookmark dall'originale.

        # apro i file con PyPDF2
        original_pdf = PdfReader(original)
        copy_pdf = PdfReader(copy)
        out_pdf = PdfWriter()

        # trasferisco le pagine dal modificato al nuovo
        for page_number in range(len(copy_pdf.pages)):
            page = copy_pdf.pages[page_number]
            out_pdf.add_page(page)

        # trasferisco i bookmark dall'originale al nuovo
        page_map = self.get_page_map(original_pdf)
        outlines = original_pdf.outline
        out_pdf = self.transfer_bookmarks(out_pdf, outlines, page_map)

        # salvo il nuovo documento
        out_pdf.write(output)

    # endregion

    def watermark(self, file):
        temp = "temp.pdf"

        # apro i file
        with (
            open(file, "rb") as file_in,
            open(constants.watermark_path, "rb") as file_watermark,
            open(temp, "wb") as file_out,
        ):
            # apro con pdfrw
            pdf_in = pdfrw.PdfReader(file_in)
            pdf_wtr = pdfrw.PdfReader(file_watermark).pages[0]
            pdf_out = pdfrw.PdfWriter()

            # scorro le pagine e applico il watermark
            num_pages = len(pdf_in.pages)
            for i in range(num_pages):
                page = pdf_in.pages[i]
                merger = pdfrw.PageMerge(page)
                # merger.add(pdf_wtr, rotate=90).render()
                # merger.add(pdf_wtr).render()
                if page.MediaBox[2] > page.MediaBox[3]:
                    # Landscape orientation
                    merger = pdfrw.PageMerge(page)
                    merger.add(pdf_wtr, rotate=90).render()
                else:
                    # Portrait orientation
                    merger = pdfrw.PageMerge(page)
                    merger.add(pdf_wtr).render()

            # salvo il pdf
            pdf_out.write(file_out, pdf_in)

        # copio i bookmark
        with (
            open(file, "rb") as file_in,
            open(temp, "rb") as f_copy,
            open("temp2.pdf", "wb") as file_out,
        ):
            self.copy_bookmarks(file_in, f_copy, file_out)

        # sostituisco il file temporaneo al nuovo
        os.replace("temp2.pdf", temp)

        # copio il file temporaneo nella cartella di output
        os.replace(temp, self.outputpath + "/" + os.path.basename(file))

    def run(self):
        if not self.overwrite:
            if os.path.isdir(self.path + "/Watermarked"):
                raise FileExistsError(
                    f"{self.path} contiene già una cartella 'Watermarked'"
                )
                exit()
            else:
                os.mkdir(self.path + "/Watermarked")
                self.outputpath = self.path + "/Watermarked"
        else:
            self.outputpath = self.path

        # get the list of files ending with .pdf in self.path using Pathlib
        pdfs_files = [
            str(file)
            for file in Path(self.path).glob("**/*.pdf")
            if str(file).endswith(".pdf")
        ]

        # run the watermark function on each pdf
        for file in pdfs_files:
            self.watermark(file)
            try:
                self.watermark(file)
            except Exception as e:
                print(f"Errore nel file {file}: {e}")
                continue
