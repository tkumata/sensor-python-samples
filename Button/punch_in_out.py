import json
import os
import random
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from gpiozero import Button

# GPIO PIN
GPIO_SIG = 15

# Timeout
TIME_OUT = 0.6

# Time while holding press and max holding time
HOLD_TIME = 3.0
HOLD_WAIT = 6.0

# flag, pressed a button
PRESSED = 0

# Get current dir.
if os.path.dirname(__file__):
    exepath = os.path.dirname(__file__) + '/'
else:
    exepath = './'

# Open config file.
f = open(exepath + 'config.json', 'r')
config_json = json.load(f)
f.close()

# Define transcripts when you are punch in.
punchInScripts = [
    'Standing by, Complete.',
    'Awakening.',
    'Ready.',
    'Clock in.',
    'Punch in.',
    '$ fg 4510ｯﾀｰﾝ'
]

# Define punch out transcripts.
punchOutScripts = [
    '3 2 1, Time out.',
    'Out of service.',
    'Clock out.',
    'Punch out.',
    'CoB today.',
    '$ shutdown -h nowｯﾀｰﾝ'
]

# Define transcripts when you are away from keyboard.
awayScripts = [
    'Exceed charge.',
    'AFK.',
    'Step out.',
    'Going on an errand.',
    'Unavailable.',
    'Ctrl + z',
    '$ bg 4510ｯﾀｰﾝ'
]


# Slack controller class
class SlackCtrl:
    def __init__(self):
        self.TOKEN = config_json['token']
        self.MEMBER_ID = config_json['member_id']
        self.CHANNEL = config_json['channel']

    def postToChannel(self, message):
        headers = {
            'Authorization': 'Bearer %s' % self.TOKEN,
            'X-Slack-User': self.MEMBER_ID,
            'Content-Type': 'application/json; charset=utf-8'
        }
        params = {
            'channel': self.CHANNEL,
            'text': message,
            'as_user': True
        }
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            method='POST',
            data=json.dumps(params).encode('utf-8'),
            headers=headers
        )
        urllib.request.urlopen(req)

    def postPunchIn(self, msg):
        self.postToChannel(':raspberrypi: ' + msg + ' :si: or :modo:')

    def postPunchOut(self, msg):
        self.postToChannel(':raspberrypi: ' + msg + ' :syu:')

    def postAway(self, msg):
        self.postToChannel(':raspberrypi: ' + msg + ' :ri:')

    def change_status(self, status_text, status_emoji):
        headers = {
            'Authorization': 'Bearer %s' % self.TOKEN,
            'X-Slack-User': self.MEMBER_ID,
            'Content-Type': 'application/json; charset=utf-8'
        }
        params = {
            'profile': {
                'status_text': status_text,
                'status_emoji': status_emoji
            }
        }
        req = urllib.request.Request(
            "https://slack.com/api/users.profile.set",
            method='POST',
            data=json.dumps(params).encode('utf-8'),
            headers=headers
        )
        urllib.request.urlopen(req)


def ljust(string, length):
    count_length = 0
    for char in string.encode().decode('utf8'):
        if ord(char) <= 255:
            count_length += 1
        else:
            count_length += 2
    return string + (length - count_length) * '.'


# Start main here.
print(ljust('Single press', 18) + '開始／再開')
print(ljust('Double press', 18) + '離席')
print(ljust('Long press', 18) + '終了')

slack = SlackCtrl()
btn = Button(GPIO_SIG, hold_time=3.0, bounce_time=0.05, pull_up=False)

while True:
    btn.wait_for_press()
    pressed_time = datetime.now()
    PRESSED = 1
    btn.wait_for_release()
    released_time = datetime.now()
    lap_time = released_time - pressed_time

    # Press type
    if (timedelta(seconds=HOLD_TIME) <= lap_time and
            lap_time <= timedelta(seconds=HOLD_WAIT)):
        # Looooong press
        now = datetime.now()
        msg = random.choice(punchOutScripts)
        slack.postPunchOut(msg)
        slack.change_status('Zzz...//終業', ':working-from-home:')
        print(now.strftime('%Y-%m-%d %H:%M:%S') + ' [held] ' + msg)
        PRESSED = 0
    if btn.wait_for_press(timeout=TIME_OUT):
        # Double press
        now = datetime.now()
        msg = random.choice(awayScripts)
        slack.postAway(msg)
        slack.change_status('AFK//離席中', ':away:')
        print(now.strftime('%Y-%m-%d %H:%M:%S') + ' [double] ' + msg)
        time.sleep(TIME_OUT)
    else:
        # Single press
        if lap_time < timedelta(seconds=0.5):
            now = datetime.now()
            msg = random.choice(punchInScripts)
            slack.postPunchIn(msg)
            slack.change_status('Working...//業務中', ':house:')
            print(now.strftime('%Y-%m-%d %H:%M:%S') + ' [single] ' + msg)
