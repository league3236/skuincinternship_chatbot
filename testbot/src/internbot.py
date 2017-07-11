# -*- coding: utf-8 -*-
from __future__ import print_function
from slackclient import SlackClient

import os
import time
import datetime
import json
import urllib2
import httplib2
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

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
EXAMPLE_COMMAND1 = "hi"
EXAMPLE_COMMAND2 = "alarm"
BL = True;

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

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

def gdrive():
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

def parse_slack(msg):
    output_list = msg
    # print(output_list)
    # print(len(output_list))

    if output_list and len(output_list) > 0:
        for output in output_list:
            #print(output)

            if output and 'text' in output and 'BOT_ID' not in output:
                command = output['text']
                answer = slack_answer(command)

             	if answer :
			slack_client.api_call(
                     		"chat.postMessage",
                     		channel=output['channel'],
                      		text=answer,
				username='인턴봇',
				as_user=True
                	)

    return None

def alarm_report():
	now = datetime.datetime.now()
	hour = now.hour
	min = now.minute
	sec = now.second;
	global BL
	if hour == 17 and min == 55 and BL:
		payload = {"username" : "주간보고서 알림", "text": "*주간 보고서를 작성하세요!!!*\nhttps://career.skuniv.ac.kr/"}
		url = "https://hooks.slack.com/services/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"
		req = urllib2.Request(url)
		req.add_header('Content-Type', 'application/json')
		urllib2.urlopen(req, json.dumps(payload))
		BL = False
	if hour == 18 and min == 1:
		BL = True
	return None


def slack_answer(txt):
    if txt == EXAMPLE_COMMAND1:
        answer = "안녕하세요! 인턴봇입니다."
    elif txt == EXAMPLE_COMMAND2:
	payload = {"username" : "주간보고서 알림", "text": "*주간 보고서*", "color" : "#36a64f", 
		"fields" : [
			{
				"title" : "주간보고서 작성 알림",
				"value" : "주간보고서를 작성하세요!!",
			}]
	}
	url = "https://hooks.slack.com/services/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"
	req = urllib2.Request(url)
	req.add_header('Content-Type', 'application/json')
	urllib2.urlopen(req, json.dumps(payload))
	return None
    else:
        return None

    return answer

if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("Connected!")
        while True:
	    alarm_report()
            parse_slack(slack_client.rtm_read())
            time.sleep(1)
    else:
        print("Connection failed.")
