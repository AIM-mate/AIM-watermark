from PyPDF2 import PdfFileReader as PyPDFReader
from PyPDF2 import PdfFileWriter as PyPDFWriter
from PyPDF2.generic import Destination
import os, pdfrw


#----- Stack overflow -----
#Presa da questa risposta: https://stackoverflow.com/a/68853751/13373369
#region

def get_page_map(bookmarkPDF, pages=None, result=None, number_pages=None):
    
    #Questa funzione costruisce un dizionario che mette in
    #corrispondenza ricorsivamente il numero della pagina e il suo
    #id (Perchè si debba fare così per i pdf non lo so ma va fatto
    #per potersi poi riferire alla pagina nelle funzioni di PyPDF2).

    if result is None:
        result = {}
    if pages is None:
        number_pages = []
        pages = bookmarkPDF.trailer["/Root"].getObject()[
            "/Pages"].getObject()
    t = pages["/Type"]
    if t == "/Pages":
        for page in pages["/Kids"]:
            result[page.idnum] = len(number_pages)
            get_page_map(bookmarkPDF, page.getObject(),
                         result, number_pages)
    elif t == "/Page":
        number_pages.append(1)
    return result

def transfer_bookmarks(out_pdf, outlines, page_map=None, parent=None):

    #Questa funzione scorre le outline del documento ricorsivamente
    #se trova una lista scorre anche quella, in caso contrario se
    #trova un bookmark con genitore glielo assegna, se no lo crea
    #sulla pagina tramite il dizionario usandone l'id come chiave
    #(+1 perchè le pagine partono da 0)
    #La risposta originale estraeva anche '/Top' e '/Left' dall'outline
    #ma ciò è valido se per i bookmark con '/Type'='/XYZ' e inoltre
    #non veniva adoperato dal codice originale, dunque l'ho cancellato.

    for outline in outlines:
        if isinstance(outline, Destination):
            outdict = {
                'title': outline['/Title'],
                'page': page_map[outline.page.idnum]+1
            }
            if parent:
                _parent = out_pdf.addBookmark(
                    title=outdict['title'],
                    pagenum=outdict['page']-1,
                    parent=parent
                )
            else:
                _parent = out_pdf.addBookmark(
                    title=outdict['title'],
                    pagenum=outdict['page']-1
                )
        elif isinstance(outline, list):
            out_pdf = transfer_bookmarks(
                out_pdf, outline, page_map, _parent)
    
    return out_pdf

def copy_bookmarks(original, copy, output):

    #Questa funzione copia le pagine dal doc modificato a quello nuovo
    #e poi trasferisce i bookmark dall'originale.

    #apro i file con PyPDF2
    original_pdf = PyPDFReader(original)
    copy_pdf = PyPDFReader(copy)
    out_pdf = PyPDFWriter()

    #trasferisco le pagine dal modificato al nuovo
    for page_number in range(copy_pdf.getNumPages()):
        page = copy_pdf.getPage(page_number)
        out_pdf.addPage(page)

    #trasferisco i bookmark dall'originale al nuovo
    page_map = get_page_map(original_pdf)
    outlines = original_pdf.getOutlines()
    out_pdf = transfer_bookmarks(out_pdf, outlines, page_map)

    #salvo il nuovo documento
    out_pdf.write(output)

#endregion

def watermark(name:str, overwrite:bool, dir:str=''):

    #creo il nome temporaneo del pdf
    temp = 'temp.pdf' if overwrite else dir+'/'*bool(dir)+'Watermarked/'+name.split('/')[-1]

    #apro i file
    with open(name, 'rb') as f_in, \
        open('aim_watermark.pdf', 'rb') as wtr, \
        open(temp, 'wb') as f_out:
        
        #apro con pdfrw
        pdf_in = pdfrw.PdfReader(f_in)
        pdf_wtr = pdfrw.PdfReader(wtr).pages[0]
        pdf_out = pdfrw.PdfWriter()

        #scorro le pagine e applico il watermark
        num_pages = len(pdf_in.pages)
        for i in range(num_pages):
            page = pdf_in.pages[i]
            merger = pdfrw.PageMerge(page)
            merger.add(pdf_wtr).render()

        #salvo il pdf
        pdf_out.write(f_out, pdf_in)

    #copio i bookmark
    with open(name,'rb') as f_in, \
        open(temp,'rb') as f_copy,\
        open('temp2.pdf','wb') as f_out:

        copy_bookmarks(f_in,f_copy,f_out)

    #sostituisco il file temporaneo al nuovo
    os.replace('temp2.pdf',temp)

    #se devo sovrascrivere sovrascrivo il vecchio col temporaneo
    if overwrite:
        os.replace(temp,name)

def waterall(pdfs,overwrite,dir=''):

    #nel caso creo la cartella 'Watermarked'
    if dir and not os.path.isdir(dir+'/Watermarked'):
        os.mkdir(dir+'/Watermarked')

    #scorro i nomi dei file e li watermarko
    for pdf in pdfs:
        try:
            watermark(pdf,overwrite,dir)
        except:
            pass
