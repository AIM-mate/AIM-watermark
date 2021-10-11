from PyPDF2 import PdfFileReader as Reader
from PyPDF2 import PdfFileWriter as Writer
from PyPDF2.generic import Destination
import os, sys, glob


#----- Stack overflow -----
#Presa da questa risposta: https://stackoverflow.com/a/68853751/13373369
#region

def get_page_map(pdf, pages=None, result=None, number_pages=None):

    #Questa funzione costruisce un dizionario che mette in
    #corrispondenza ricorsivamente il numero della pagina e il suo
    #id (Perchè si debba fare così per i pdf non lo so ma va fatto
    #per potersi poi riferire alla pagina nelle funzioni di PyPDF2).

    if result is None:
        result = {}
    if pages is None:
        number_pages = []
        pages = pdf.trailer["/Root"].getObject()["/Pages"].getObject()
    t = pages["/Type"]
    if t == "/Pages":
        for page in pages["/Kids"]:
            result[page.idnum] = len(number_pages)
            get_page_map(pdf, page.getObject(), result, number_pages)
    elif t == "/Page":
        number_pages.append(1)
    return result


def transfer_bookmarks(pdf_out, outlines, page_map=None, parent=None):

    #Questa funzione scorre le outline del documento ricorsivamente
    #se trova una lista scorre anche quella, in caso contrario se
    #trova un bookmark con genitore glielo assegna, se no lo crea 
    #sulla pagina tramite il dizionario usandone l'id come chiave
    #(+1 perchè le pagine partono da 0) 
    #La risposta originale estraeva anche '/Top' e '/Left' dall'outline 
    #ma ciò è valido se per i bookmark con '/Type'='/XYZ' e inoltre
    #non veniva adoperato dal codice originale, dunque l'ho cancellato.

    for outline in outlines:
        print(outline)
        if isinstance(outline, Destination):
            outdict = {
                'title': outline['/Title'],
                'page': page_map[outline.page.idnum]+1
            }
            if parent:
                _parent = pdf_out.addBookmark(
                    title=outdict['title'],
                    pagenum=outdict['page']-1,
                    parent=parent
                )
            else:
                _parent = pdf_out.addBookmark(
                    title=outdict['title'],
                    pagenum=outdict['page']-1
                )
        elif isinstance(outline, list):
            pdf_out = transfer_bookmarks(
                pdf_out, outline, page_map, _parent)
    return pdf_out

#endregion

def watermark(name):

    temp = 'watermarked.pdf'

    with open(name, 'rb') as f_in, \
        open('aim_watermark.pdf', 'rb') as wtr, \
        open(temp, 'wb') as f_out:
        
        print('Apro il file')
        pdf_in = Reader(f_in)
        pdf_wtr = Reader(wtr).getPage(0)
        pdf_out = Writer()

        num_pages = pdf_in.getNumPages()
        for i in range(num_pages):
            percent = int(100*round( (i+1)/num_pages, 2) )
            printProgressBar(percent, 'Filigrana')
            page = pdf_in.getPage(i)
            page.mergePage(pdf_wtr)
            pdf_out.addPage(page)

        print('\n Copio i segnalibri')
        
        page_map = get_page_map(pdf_in)
        outlines = pdf_in.getOutlines()

        pdf_out = transfer_bookmarks(pdf_out, outlines, page_map)

        pdf_out.write(f_out)

    os.replace(temp,name)
    print('Finito')

def waterall():

    pdfs = [file for file in glob.iglob('**/**', recursive=True) \
        if file.split('.')[-1] == 'pdf' \
            and file != 'aim_watermark.pdf' \
                and 'Watermarkati' not in file
        ]

    for pdf in pdfs:
        print('Aggiungo filigrana a '+pdf)
        try:
            watermark(pdf)
        except:
            print('Fallito')


def printProgressBar(value, label):
    n_bar = 40  # size of progress bar
    max = 100
    j = value/max
    sys.stdout.write('\r')
    bar = '█' * int(n_bar * j)
    bar = bar + '-' * int(n_bar * (1-j))

    sys.stdout.write(f"{label.ljust(10)} | [{bar:{n_bar}s}] {int(100 * j)}% ")
    sys.stdout.flush()

#if __name__=='__main__':
#    waterall()
