import json
import os
import urllib.parse
import urllib.request
from signal import pause

from gpiozero import Button

Button.was_held = False
GPIO_SIG = 15

# Get current dir.
if os.path.dirname(__file__):
    exepath = os.path.dirname(__file__) + '/'
else:
    exepath = './'

# Open config file.
f = open(exepath + 'config.json', 'r')
config_json = json.load(f)
f.close()


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

    def postPunchIn(self):
        self.postToChannel(':raspberrypi:＜業務開始します。')

    def postPunchOut(self):
        self.postToChannel(':raspberrypi:＜業務終了します。')

    def postAway(self):
        self.postToChannel(':raspberrypi:＜AFK')


def held(btn):
    btn.was_held = True
    # print("held")
    slack.postPunchOut()


def released(btn):
    if not btn.was_held:
        pressed()
    btn.was_held = False


def pressed():
    # print("press once")
    slack.postPunchIn()


btn = Button(GPIO_SIG, hold_time=3, bounce_time=0.05, pull_up=False)
slack = SlackCtrl()

print('一回押し＝出勤')
print('押し維持＝退勤')

btn.when_held = held
btn.when_released = released

pause()
