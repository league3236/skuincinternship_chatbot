#!/usr/bin/env python
#coding=utf8
"""
====================================
 :mod:`sendslack` Slack 채팅 프로그램에 자동으로 메시지 전달
====================================
.. moduleauthor:: 채문창 <mcchae@gmail.com>
.. note:: MIT License
"""

################################################################################
import os
import sys
import signal
import getopt
import logging
import logging.handlers
import traceback
import json
from termcolor import colored
from slacker import Slacker


################################################################################
logger = None


################################################################################
def get_logger(projname, root_folder='/opt/FutureServer',
               logsize=500*1024, logbackup_count=4):
    logdir = root_folder  # '%s/%s' % (root_folder, projname)
    if not os.path.exists(logdir):
        # noinspection PyBroadException
        try:
            os.makedirs(logdir)
        except:
            logdir = '/tmp/%s' % projname
            if not os.path.exists(logdir):
                os.makedirs(logdir)
    logfile='%s/%s.log' % (logdir, projname)
    loglevel = logging.INFO
    _logger = logging.getLogger(projname)
    _logger.setLevel(loglevel)
    if _logger.handlers is not None and len(_logger.handlers) >= 0:
        for handler in _logger.handlers:
            _logger.removeHandler(handler)
        _logger.handlers = []
    loghandler = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=logsize, backupCount=logbackup_count)
    formatter = logging.Formatter(
        '%(asctime)s-%(name)s-%(levelname)s-%(message)s')
    loghandler.setFormatter(formatter)
    _logger.addHandler(loghandler)
    return _logger


################################################################################
def receive_signal(signum, _):
    """시그널 핸들러
    """
    if signum in [signal.SIGTERM, signal.SIGHUP, signal.SIGINT]:
        logger.info('Caught signal %s, exiting.' % (str(signum)))
        sys.exit()
    else:
        logger.info('Caught signal %s, ignoring.' % (str(signum)))


################################################################################
def sendmsg(**kwargs):
    token = kwargs['json']['token']
    channel = None
    for chandic in kwargs['json']['channels']:
        if chandic['name'] == kwargs['channel']:
            channel = chandic
            break
    if not channel:
        raise ReferenceError('Cannot find channel named <%s> from json config'
                             % kwargs['channel'])
    if not kwargs['icon_emoji']:
        kwargs['icon_emoji'] = channel['icon_emoji']
    slack = Slacker(token, incoming_webhook_url=channel['incoming_webhook_url'])
    # max length of text at slack may be 4,000
    txtlen = 3990 - len(kwargs['title'])
    if len(kwargs['text']) > txtlen:
        text = '*%s*' % kwargs['title']
        slack.chat.post_message(channel['name'], text,
                                username=kwargs['user_name'],
                                icon_emoji=kwargs['icon_emoji'],
                                )
        aggtxt = ""
        for line in kwargs['text'].split('\n'):
            if len(aggtxt) + len(line) > txtlen:
                slack.chat.post_message(channel['name'], '```%s```' % aggtxt,
                                        username=kwargs['user_name'],
                                        icon_emoji=kwargs['icon_emoji'],
                                        )
                aggtxt = ''
            aggtxt += line
        if len(aggtxt) > 0:
            slack.chat.post_message(channel['name'], '```%s```' % aggtxt,
                                    username=kwargs['user_name'],
                                    icon_emoji=kwargs['icon_emoji'],
                                    )
    else:
        text = '*%s*\n```%s```' \
               % (kwargs['title'], kwargs['text'])
        slack.chat.post_message(channel['name'], text,
                                username=kwargs['user_name'],
                                icon_emoji=kwargs['icon_emoji'],
                                )
    # 파일 업로드는 잘 안되었음
    # if kwargs['text_file'] and os.path.exists(kwargs['text_file']):
    #     # slack.files.upload(kwargs['text_file'],
    #     #                    channels=slack.channels.get_channel_id(channel['name']))
    #     r = slack.files.upload(kwargs['text_file'])
    #     pass


################################################################################
def usage(msg=None):
    """사용방법 출력
    """
    if msg:
        sys.stderr.write(colored('Error: %s!!!\n' % msg, 'red'))
    prog = sys.argv[0]
    sys.stderr.write(colored('''
Usage: {prog} [options]
  send a message to slack channel
options:
    -h, --help : print this help message
    -c, --config : set json config file
     (default is sendslack.json in which same folder of this program is located)
    -l, --channel : specify channel (do not skip)
    -t, --title : message title
    -x, --text : message body parameter
    -f, --text_file : message body
    -u, --user_name : user name
    -j, --icon_emoji : set icon imogi (eg. :cow: )
'''.format(prog=prog), 'green'))
    sys.exit(1)


################################################################################
if __name__ == '__main__':
    # signal handler
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, receive_signal)
    signal.signal(signal.SIGHUP, receive_signal)
    signal.signal(signal.SIGINT, receive_signal)
    # parsing commmand lines
    kwargs = {
        'json': None,
        'config': None,
        'channel': None,
        'title': None,
        'text': None,
        'text_file': None,
        'user_name': None,
        'icon_emoji': None,
    }
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:l:t:x:f:u:j:",
                                   ["help", "config=",
                                    "channel=", "title=",
                                    "text=", 'text_file=', 'user_name=',
                                    "icon_emoji="])
        for o, a in opts:
            if o in ("-h", "--help"):
                usage()
            elif o in ("-c", "--config"):
                kwargs['config'] = a
            elif o in ("-l", "--channel"):
                kwargs['channel'] = a
            elif o in ("-t", "--title"):
                kwargs['title'] = a
            elif o in ("-x", "--text"):
                kwargs['text'] = a
            elif o in ("-f", "--text_file"):
                kwargs['text_file'] = a
            elif o in ("-u", "--user_name"):
                kwargs['user_name'] = a
            elif o in ("-j", "--icon_emoji"):
                kwargs['icon_emoji'] = a

        logger = get_logger('sendslack', root_folder='/tmp')
        if not kwargs['config']:
            sc_dir = os.path.dirname(os.path.realpath(__file__))
            kwargs['config'] = '%s/sendslack.json' % sc_dir
        if not os.path.exists(kwargs['config']):
            raise IOError('Cannot read config file <%s>' % kwargs['config'])
        with open(kwargs['config']) as ifp:
            kwargs['json'] = json.load(ifp)
        if not kwargs['channel']:
            raise ValueError('-l, --channel channel needed!')
        if not kwargs['title']:
            raise ValueError('-t, --title title needed!')
        if not (kwargs['text'] or kwargs['text_file']):
            raise ValueError('-x, --text or -f, --text_file needed!')
        if kwargs['text_file']:
            with open(kwargs['text_file']) as ifp:
                kwargs['text'] = ifp.read()

        sendmsg(**kwargs)
    except Exception as e:
        exc_info = sys.exc_info()
        out = traceback.format_exception(*exc_info)
        del exc_info
        logger.error("%s\n" % ''.join(out))
        logger.error('Error:%s'%str(e))
        usage(str(e))
