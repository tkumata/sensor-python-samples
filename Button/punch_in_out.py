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
TIME_OUT = 0.5

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
    'Out of service, today.',
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
    '$ Ctrl + z',
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

    def changeStatus(self, status_text, status_emoji):
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

    def postPunchIn(self, msg):
        self.postToChannel(':raspberrypi:' + msg + ':si: or :modo:')
        self.changeStatus(':raspberrypi:Working//業務中', ':working-from-home:')

    def postPunchOut(self, msg):
        self.postToChannel(':raspberrypi:' + msg + ':syu:')
        self.changeStatus(':raspberrypi:Zzz.//終業', ':syu:')

    def postAway(self, msg):
        self.postToChannel(':raspberrypi:' + msg + ':ri:')
        self.changeStatus(':raspberrypi:AFK//離席中', ':ri:')


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
# btn = Button(GPIO_SIG, hold_time=3.0, bounce_time=0.05, pull_up=False)
btn = Button(GPIO_SIG, hold_time=3.0, pull_up=False)

try:
    while True:
        # when press button
        btn.wait_for_press()
        pressed_time = datetime.now()

        # when release button
        btn.wait_for_release()
        released_time = datetime.now()

        # get lap time between pressed and released
        lap_time = released_time - pressed_time

        # Looooong press
        if (timedelta(seconds=HOLD_TIME) <= lap_time and
                lap_time <= timedelta(seconds=HOLD_WAIT)):
            msg = random.choice(punchOutScripts)
            slack.postPunchOut(msg)

            now = datetime.now()
            print(now.strftime('%Y-%m-%d %H:%M:%S') + ' [held] ' + msg)

        # Double press
        if btn.wait_for_press(timeout=TIME_OUT):
            msg = random.choice(awayScripts)
            slack.postAway(msg)

            now = datetime.now()
            print(now.strftime('%Y-%m-%d %H:%M:%S') + ' [double] ' + msg)
            time.sleep(TIME_OUT)
        else:
            if lap_time < timedelta(seconds=0.5):
                # Single press
                msg = random.choice(punchInScripts)
                slack.postPunchIn(msg)

                now = datetime.now()
                print(now.strftime('%Y-%m-%d %H:%M:%S') + ' [single] ' + msg)

except KeyboardInterrupt:
    print('Keyboard interrupt.')
    exit()
