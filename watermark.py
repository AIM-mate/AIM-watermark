from PyPDF2 import PdfFileWriter, PdfFileReader
import os, sys, glob

def watermark(name):

    temp = 'watermarked.pdf'

    with open(name, 'rb') as f_in, \
        open('aim_watermark.pdf', 'rb') as wtr, \
        open(temp, 'wb') as f_out:
        
        print('Apro il file')
        pdf_in = PdfFileReader(f_in)
        pdf_wtr = PdfFileReader(wtr).getPage(0)
        pdf_out = PdfFileWriter()

        num_pages = pdf_in.getNumPages()
        for i in range(num_pages):
            percent = int(100*round( (i+1)/num_pages, 2) )
            printProgressBar(percent, name)
            page = pdf_in.getPage(i)
            page.mergePage(pdf_wtr)
            pdf_out.addPage(page)

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

if __name__=='__main__':
    waterall()
