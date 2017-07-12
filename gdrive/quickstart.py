from __future__ import print_function
import httplib2
import os
import io

from googleapiclient.http import *
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    #results = service.files().list(
    #    pageSize=30,fields="nextPageToken, files(id, name)").execute()
    results = service.files().list(corpora="teamDrive", includeTeamDriveItems=True, supportsTeamDrives=True, teamDriveId="0AElQsZ-ZfPD-Uk9PVA").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        list = []
        for item in items:
            if item['name'].find('OJT') != -1:
                item['name'] = item['name'].split(' ')[0].encode('utf-8')
                item['id'] = item['id'].encode('utf-8')
                map = {'name' : item['name'], 'id' : item['id']}
                list.append(map)
        for item in list :
            print('{0} ({1})'.format(item['name'], item['id']))
                #print('{0} ({1})'.format(item['name'], item['id']))
            #request = service.files().get_media(fileId=item['id'])
            #fh = io.FileIO(item['name'], mode='wb')
            #downloader = MediaIoBaseDownload(fh, request)
            #done = False
        #while done is False:
            #status, done = downloader.next_chunk()
            #print ("Download %d%%." % int(status.progress() * 100))



if __name__ == '__main__':
    main()
