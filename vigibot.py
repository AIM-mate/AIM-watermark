#importo tutto
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import PyPDF2
import os

#variabili
id = '1n7cyj2H-pQT-TyTWSkbot7aAbLccCW3Y'

#funzioni:

#recursive branding
def brandall(id):
    files = drive.ListFile({'q': "'%s' in parents and trashed=false" %id}).GetList()
    for file in files:
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            brandall(file['id'])
        elif file['title'].rsplit('.')[-1]=='pdf':
            brand(file['id'])

#adding the watermark to each page
def watermark(file):

    #opening the files
    pdf_file = open(file, 'rb')
    watermark_file = open('aim_watermark.pdf', 'rb')

    
    #opening the pdfs
    pdfin = PyPDF2.PdfFileReader(pdf_file)
    watermark = PyPDF2.PdfFileReader(watermark_file).getPage(0)
    pdfout = PyPDF2.PdfFileWriter()

    #adding the watermark
    for i in range(pdfin.getNumPages()):
        page = pdfin.getPage(i)
        page.mergePage(watermark)
        pdfout.addPage(page)
    
    #sovrascrivo il pdf
    pdf = open(file,'wb')
    pdfout.write(pdf)

    #closing the files
    pdf.close()
    watermark_file.close()
    pdf_file.close()

#download, brand, upload and delete from local directory
def brand(id):
    #downloading the file
    file = drive.CreateFile({'id': id})
    file.GetContentFile(file['title'])

    #adding the watermark
    watermark(file['title'])

    #uploading the file
    file = drive.CreateFile({'id': id})
    file.SetContentFile(file['title'])
    file.Upload()

    #deliting from the local directories
    file = open(file['title'],'r')
    file.close()
    os.remove(file.name)

#moving every file to right directories
def moveall(id):
    files = drive.ListFile(
        {'q': "'%s' in parents and trashed=false" % id}).GetList()
    for file in files:
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            moveall(file['id'])
        else:
            to = sort(file['title'])
            move(file['id'],to)
#moving files in google drive
def move(id, to):
    #apro il file, scarico e cancello
    fromfile = drive.CreateFile({'id': id})
    fromfile.GetContentFile(fromfile['title'])
    fromfile.Trash()

    #creo il file di destinazione e lo carico
    tofile = drive.CreateFile({'parents': [{'id':to}]})
    tofile.SetContentFile(fromfile['title'])
    tofile.Upload()

    #elimino e rimuovo
    name = fromfile['title']
    del fromfile
    del tofile
    os.remove(name)

#sorting files into the right directories
def sort(fltitle):
    #salvo il titolo senza poi modificarlo direttamente
    title=fltitle
    #variabili di default
    sub = '1D8ScM96Oy-7NUywk_NuE6qlB3DWBiOwD'

    #dizionario coi valori delle varie materie
    subjects = {
        'ANALISI 1': '1yFXmS-XsrH0IFYO-ZXGcbJhdPL7AKTg5',
        'ANALISI I': '1yFXmS-XsrH0IFYO-ZXGcbJhdPL7AKTg5',
        'CHIMICA': '1vEap1KLHh8nOOhYp0aImlLnubohgLMik',
        'INFORMATICA': '1vmYYJYRxEf0-SWRxGuq3KbWJiU1eb1BS',
        'FISICA 1': '1hEawaPSRpbvCx5S3mHYl0wZ275Yzu_mu',
        'FISICA I': '1hEawaPSRpbvCx5S3mHYl0wZ275Yzu_mu',
        'ECONOMIA': '11ecACdbf7-oP2t8fVdxYRUxbmmWjeoxw',
        'STATISTICA': '1W6Yp8KTsonISENgk4zoghFogOtYQ3AoE',
        'GEOMETRIA ALGEBRA LINEARE': '1nztJrRH8BOZoo3W-qZg0YwPHyxVJNKOk',
        'GAL': '1nztJrRH8BOZoo3W-qZg0YwPHyxVJNKOk',
        'ANALISI 2': '1xgmiP7oXsqCL7y1IrQ8JN7UeEf2EjQRa',
        'ANALISI II': '1xgmiP7oXsqCL7y1IrQ8JN7UeEf2EjQRa',
        'FISICA 2': '1RQ1JKTojMBj4NjPIbyqDsn8MLYlTYITV',
        'FISICA II': '1RQ1JKTojMBj4NjPIbyqDsn8MLYlTYITV',
        'ELETTROTECNICA': '1VRmIX_B7aXO66ClMXynmFb-LFuQ2WVkF',
        'AUTOMATICA': '1NAIG5kv3FXFRKc1IO8R04C09lRw3OMiq',
        'PROBABILITA': '1K3fjC8TulagdBJLH3BLMfAl46KzAKJfb',
        'NUMERICA': '13Ydgs8F0N3M5ITB2bwDPWkd3axAGbW_6',
        'ANALISI 3': '1rEBU3s-oRR4nFeg_EIpYNVQrUwl_XBZU',
        'ANALISI III': '1rEBU3s-oRR4nFeg_EIpYNVQrUwl_XBZU',
        'MECCANICA': '178Qimcb-MihkmFa3jHS6UqOFGJFxpgD_'
    }
    #buzzwords da rimuovere
    buzzwords = [
        'LEZIONE',
        'LABORATORIO',
        'APPUNTI',
        'ESERCIZI',
        'ESERCITAZIONE',
        'DI',
        'PDF',
        'TXT',
        'FINANZA',
        'IMPRESA',
        'BILANCIO',
        'DECISION',
        'MAKING',
        'E',
        'ESERCITAZIONI',
        'LEZIONI',
        'LABORATORI',
        'M'
    ]

    #pulisco il titolo dai divisori
    title = clean(title)
    #cerco la materia e nel caso la toglie
    for subject in subjects.keys():
        if subject in title.upper():
            sub = subjects[subject]
            nt=''
            for x in title.split():
                if x.upper() not in subject:
                    nt = nt + x + ' '
            title = nt
    #pulisco dalle buzzwords:
    nt=''
    for x in title.split():
        if x.upper() not in buzzwords and not x.isdigit():
            nt = nt + x + ' '
    title = nt
    #vedo se il nome esiste già nella directory
    files = drive.ListFile(
        {'q': "'%s' in parents and trashed=false" % sub}).GetList()
    for file in files:
        if file['mimeType'] == 'application/vnd.google-apps.folder' and file['title'] == title:
            return file['id']
    if len(title)>0:
        file = drive.CreateFile({'title': title, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [
                         {'id': sub}]})
        file.Upload()
        return file['id']
    else:
        for file in files:
            if file['title'] == 'Varie':
                return file['id']
            
#pulisco la parola da segnin vari di separazione
def clean(title):
    out=''
    signs = ['-', '_', ' ', '.','/']
    for x in title:
        if x not in signs:
            out = out + x
        else:
            out = out + ' '
    return out    

    
    

    
            
    




#svolgimento:

#accedo al drive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


brandall(id)
moveall(id)

























