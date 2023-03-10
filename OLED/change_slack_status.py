import json
import os
import subprocess
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import datetime

import board
import digitalio
import RPi.GPIO as GPIO
from adafruit_rgb_display import ssd1351  # pylint: disable=unused-import
from PIL import Image, ImageDraw, ImageFont

# Get current dir.
if os.path.dirname(__file__):
    exepath = os.path.dirname(__file__) + '/'
else:
    exepath = './'

# Open config file.
f = open(exepath + 'config.json', 'r')
config_json = json.load(f)
f.close()


# Configuration for CS and DC pins (these are PiTFT defaults):
print('Setup PIN...')
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config a ultrasonic SIG pin:
GPIO_SIG = 17

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
print('new SPI...')
spi = board.SPI()

# pylint: disable=line-too-long
# Create the display:
print('Creating display...')
disp = ssd1351.SSD1351(
    spi,
    rotation=180,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Create image for drawing.
# Make sure to create imageBase with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

# Create a image, black color.
print('Creating a black image...')
imageBlack = Image.new("RGB", (width, height))
drawBalck = ImageDraw.Draw(imageBlack)
drawBalck.rectangle((0, 0, width, height), outline=0, fill=0)
imageBlended = imageBlack.copy()

# First define some constants to allow easy positioning of text.
padding = -2
x = 0

# Load a TTF font.
defaultFont = ImageFont.truetype(
    os.path.dirname(__file__) +
    "/materials/SFMono-Regular-Nerd-Font-Complete.otf",
    14
)
smallFont = ImageFont.truetype(
    os.path.dirname(__file__) +
    "/materials/SFMono-Regular-Nerd-Font-Complete.otf",
    12
)
largeFont = ImageFont.truetype(
    os.path.dirname(__file__) +
    "/materials/SFMono-Regular-Nerd-Font-Complete.otf",
    26
)


class SlackCtrl:
    def __init__(self):
        self.TOKEN = config_json['token']
        self.MEMBER_ID = config_json['member_id']

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
        # with urllib.request.urlopen(req) as res:
        #     print(json.dumps(json.loads(
        #         res.read().decode('utf-8')),
        #         indent=2)
        #     )

        i = 0
        while True:
            try:
                urllib.request.urlopen(req)
            except HTTPError as e:
                if i + 1 == 3:
                    raise
                else:
                    print('Error code: ', e.code)
            except URLError as e:
                print('Reason: ', e.reason)
            else:
                break


class RaspiCtrl:
    def measurementInCM(self):
        # Setup the GPIO_SIG as output
        GPIO.setup(GPIO_SIG, GPIO.OUT)

        # Warming up
        GPIO.output(GPIO_SIG, GPIO.LOW)
        time.sleep(0.2)
        GPIO.output(GPIO_SIG, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(GPIO_SIG, GPIO.LOW)
        start = time.time()

        # Setup GPIO_SIG as input
        GPIO.setup(GPIO_SIG, GPIO.IN)

        # Get duration from ultrasonic SIG pin
        while GPIO.input(GPIO_SIG) == 0:
            start = time.time()

        while GPIO.input(GPIO_SIG) == 1:
            stop = time.time()

        return self.measurementPulse(start, stop)

    def measurementPulse(self, start, stop):
        # Calculate pulse length
        elapsed = stop - start

        # Distance pulse travelled in that time is time
        # multiplied by the speed of sound (cm/s)
        distance = elapsed * 34300

        # That was the distance there and back so halve the value
        distance = distance / 2

        return distance


print('Ready to display screen. Look the OLED.')

raspi = RaspiCtrl()
slack = SlackCtrl()

at_counter = 0
no_counter = 0
status = 0
COUNTER_THRESHOLD = 3
DISTANCE_THRESHOLD = 55

DIST_ICON = u'\ufaca'
DESK_ICON = u'\ufb5a'
CLOCK_ICON = u'\ue38b'
TEMP_ICON = u'\uf2c9'
CPU_ICON = u'\ue266'
RASPI_ICON = u'\ue722'
CALENDER_ICON = u'\uf073'

while True:
    try:
        # Get a measurement distance.
        distance = raspi.measurementInCM()
        distanceSlack = "%.1f" % distance
        distanceLabel = DIST_ICON + "%.1f cm" % distance

        if distance < DISTANCE_THRESHOLD:
            at_counter = at_counter + 1
            no_counter = 0
        else:
            no_counter = no_counter + 1

        if at_counter > COUNTER_THRESHOLD and status == 0:
            now = datetime.now()
            status = 1
            slack.change_status(
                "At the desk:raspberrypi:" + distanceSlack + "cm",
                ":house:"
            )
            at_counter = 0
            no_counter = 0
            print(now.strftime('%Y-%m-%d %H:%M:%S') + ' at the desk')

        if no_counter > COUNTER_THRESHOLD and status == 1:
            now = datetime.now()
            status = 0
            slack.change_status(
                "AFK:raspberrypi:" + distanceSlack + "cm",
                ":away:"
            )
            at_counter = 0
            no_counter = 0
            print(now.strftime('%Y-%m-%d %H:%M:%S') + ' AFK')

        # Copy new background
        copyBaseImage = imageBlended.copy()

        # Get drawing object to draw on copyBaseImage.
        draw = ImageDraw.Draw(copyBaseImage)

        # Get time
        cmd = "date '+%H:%M'"
        timePresent = subprocess.check_output(cmd, shell=True).decode("utf-8")
        timePresent = CLOCK_ICON + timePresent

        # Get date.
        cmd = "date '+%Y/%m/%d'"
        dateToday = subprocess.check_output(cmd, shell=True).decode("utf-8")
        dateToday = CALENDER_ICON + dateToday

        # Get a Pi model data.
        cmd = "grep </proc/cpuinfo '^Model' | cut -d':' -f2 | cut -d' ' -f2-"
        raspiModel = subprocess.check_output(cmd, shell=True).decode("utf-8")
        raspiModel = RASPI_ICON + raspiModel

        # Get a CPU load data.
        cmd = "top -bn1 | grep load | awk '{printf \"%.2f\", $(NF-2)}'"
        cpuLoad = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cpuLoad = CPU_ICON + cpuLoad

        # Get a CPU temparature.
        cmd = "cat /sys/class/thermal/thermal_zone0/temp"\
            + " | awk '{printf \"%.1f C\", $(NF-0) / 1000}'"
        cpuTemp = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cpuTemp = TEMP_ICON + cpuTemp

        # Set a y-scale padding.
        y = padding

        # Draw Raspi model.
        draw.text((x, y), raspiModel, font=defaultFont, fill="#bc1142")
        y += defaultFont.getsize(raspiModel)[1]

        # Draw time.
        x = (width / 2) - (largeFont.getsize(timePresent)[0] / 2)
        draw.text((x, y), timePresent, font=largeFont, fill="white")
        y += largeFont.getsize(timePresent)[1]

        # Draw date.
        x = (width / 2) - (smallFont.getsize(dateToday)[0] / 2)
        draw.text((x, y), dateToday, font=smallFont, fill="white")
        y += smallFont.getsize(dateToday)[1]

        x = 0

        # Draw CPU info.
        draw.text((x, y), cpuLoad, font=defaultFont, fill="white")
        y += defaultFont.getsize(cpuLoad)[1]
        draw.text((x, y), cpuTemp, font=defaultFont, fill="white")
        y += defaultFont.getsize(cpuTemp)[1]

        # Draw measurement distance as string.
        draw.text((x, y), distanceLabel, font=defaultFont, fill="white")
        y += defaultFont.getsize(distanceLabel)[1]

        # Draw my status.
        if status == 1:
            draw.text(
                (x, y),
                DESK_ICON + "At the desk.",
                font=smallFont,
                fill="white"
            )
        else:
            draw.text(
                (x, y),
                DESK_ICON + "AFK",
                font=smallFont,
                fill="white"
            )

        # Display imageBase.
        disp.image(copyBaseImage)
        time.sleep(1)

    except KeyboardInterrupt:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        disp.image(copyBaseImage)
        GPIO.cleanup()
        print('Keyboard interrupt.')
        exit()
