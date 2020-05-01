from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

#accedo al drive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


def listall(id, list):
    files = drive.ListFile({'q': "'%s' in parents and trashed=false" % id}).GetList()
    for file in files:
        if file['mimeType'] == 'application/vnd.google-apps.folder':  # if folder
            list.append((file['title'],file['id']))
            listall(file['id'], list)
        else:
            list.append((file['title'], file['id']))

list=[]
listall('root',list)
for item in list:
    print(item)
