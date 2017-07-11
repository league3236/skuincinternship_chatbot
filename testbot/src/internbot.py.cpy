# -*- coding: utf-8 -*-

import os
import time
import datetime
import json
import urllib2
from slackclient import SlackClient


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
	if hour == 18 and min == 01:
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