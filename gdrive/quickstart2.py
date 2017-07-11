from __future__ import print_function
import httplib2
import os
import io
import sys
import re
import html

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
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
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
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    #input -> unicode
    st = '문서'                                    
    pre = '&#'                                   
    suf = ';'                                    
    result = ''                                  
    for stt in st:                               
    	if ord(stt) == 32:                       
        	result += ' '                        
    	else:                                    
        	result += (pre + str(ord(stt)) + suf)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    #results = service.files().list(
    #    pageSize=30,fields="nextPageToken, files(id, name)").execute()
    #results = service.files().list(corpora="teamDrive", includeTeamDriveItems=True, supportsTeamDrives=True, teamDriveId="0AElQsZ-ZfPD-Uk9PVA").execute()
    results = service.files().export(fileId="1a1l_QdFvqgtKK0lO3zXeTOjnJwpvfKzs8MQQ55yxs_s", mimeType="text/html").execute(http=http)
    # print(results)
    # search Keywork in Streaming data
    results = results.decode("utf-8")	# without this line, Printing Error!!
    p = re.compile((u'<h[0-9] id="(.*?)"|<span style="color:#\d+;font-weight:\d+;text-decoration:none;vertical-align:baseline;font-size:\d+pt;font-family:&quot;Malgun Gothic&quot;;font-style:normal">(.*?)<\/span>'), re.UNICODE)
    findAll = p.findall(results)
    content = ''
    head_id = ''
    for i in findAll:                                                     
          if i[0]:
              if content and re.search(u''+result, content):
                 print("URL : " + head_id + "\n" + html.unescape(content) + "\n\n")
              head_id = i[0]
              content = ''
          else :
              content += '\n' + i[1]
 
if __name__ == '__main__':
    main()

