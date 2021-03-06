# -*- coding: utf-8 -*-
from __future__ import print_function
from slackclient import SlackClient
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib import *
from slacker import Slacker

import os
import time
import datetime
import json
import http.client
import re
import html
import urllib

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

# constants
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'
BOT_ID = os.environ.get("BOT_ID")
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
EXAMPLE_COMMAND1 = "hi"
EXAMPLE_COMMAND2 = "alarm"
OJT_COMMAND = "ojt찾아줘"
BL = True;
slack = Slacker(os.environ.get("SLACK_BOT_TOKEN"))
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def post_to_channel(message):
    slack.chat.post_message('chatbot_test', message, as_user=True)

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'drive-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def gdrive(keyword):
    st = keyword
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
    results = service.files().export(fileId="1a1l_QdFvqgtKK0lO3zXeTOjnJwpvfKzs8MQQ55yxs_s", mimeType="text/html").execute(http=http)
    results = results.decode("utf-8")	# without this line, Printing Error!!
    p = re.compile((u'<h[0-9] id="(.*?)"|<span style="color:#\d+;font-weight:\d+;text-decoration:none;vertical-align:baseline;font-size:\d+pt;font-family:&quot;Malgun Gothic&quot;;font-style:normal">(.*?)<\/span>'), re.UNICODE)
    findAll = p.findall(results)
    content = ''
    head_id = ''
    count = 0
    for i in findAll:
        if i[0]:
            if content and re.search(u''+result, content):
                count += 1
                answer = "*•"+str(count)+"번쨰 검색 결과*\n"+"```"+html.unescape(content)+"\n"+"[링크] "+"https://docs.google.com/document/d/1a1l_QdFvqgtKK0lO3zXeTOjnJwpvfKzs8MQQ55yxs_s/edit#heading="+head_id+"```"
                post_to_channel(answer)
            head_id = i[0]
            content = ''
        else :
            content += '\n' + i[1]
    post_to_channel('총 '+str(count)+'개의 검색 결과를 찾았습니다.')

def parse_slack(msg):
    output_list = msg
    print(output_list)
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and 'BOT_ID' not in output:
                command = output['text']    # Get text in JSON
                answer = slack_answer(command)    # Go to desk
                if answer :
                    post_to_channel(answer)
    return None

def alarm_report():
    now = datetime.datetime.now()
    hour = now.hour
    min = now.minute
    sec = now.second;
    global BL
    if hour == 17 and min == 55 and BL:
        post_to_channel("*주간보고서 알림*\n```주간보고서를 작성하세요!!!```\nhttps://career.skuniv.ac.kr/")
        BL = False
    if hour == 18 and min == 1:
        BL = True
    return None


def slack_answer(txt):    # Have Condition
    if txt == EXAMPLE_COMMAND1:
        answer = "안녕하세요! 인턴봇입니다."
    elif txt == EXAMPLE_COMMAND2:
        post_to_channel('*알림알림*');
        return None
    elif txt.find(OJT_COMMAND) != -1:
        gdrive(txt[7:])
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
