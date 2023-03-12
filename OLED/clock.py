import os
import subprocess
import time

import board
import digitalio
from adafruit_rgb_display import ssd1351
from PIL import Image, ImageDraw, ImageFont

print('Setup PIN...')
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

print('new SPI...')
spi = board.SPI()

print('Creating a display...')
BAUDRATE = 24000000
disp = ssd1351.SSD1351(
    spi,
    rotation=180,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

print('Adjusting up and bottom on screen...')
if disp.rotation % 180 == 90:
    height = disp.width
    width = disp.height
else:
    width = disp.width
    height = disp.height

print('Creating a black image...')
baseImage = Image.new("RGB", (width, height))
drawedBaseImage = ImageDraw.Draw(baseImage)
drawedBaseImage.rectangle((0, 0, width, height), outline=0, fill=0)
draw = ImageDraw.Draw(baseImage)

# First define some constants to allow easy positioning of text.
padding = -2
x = 0

# Load a TTF font.
smallFont = ImageFont.truetype(
    os.path.dirname(__file__) +
    "/materials/SFMono-Regular-Nerd-Font-Complete.otf",
    12
)
defaultFont = ImageFont.truetype(
    os.path.dirname(__file__) +
    "/materials/SFMono-Regular-Nerd-Font-Complete.otf",
    14
)
largeFont = ImageFont.truetype(
    os.path.dirname(__file__) +
    "/materials/SFMono-Regular-Nerd-Font-Complete.otf",
    20
)

DIST_ICON = u'\ufaca '
DESK_ICON = u'\ufb5a '
CLOCK_ICON = u'\ue38b '
TEMP_ICON = u'\uf2c9 '
CPU_ICON = u'\ue266 '
RASPI_ICON = u'\ue722 '
CALENDER_ICON = u'\uf073 '

try:
    while True:
        y = padding

        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Get a Pi model data.
        cmd = "grep </proc/cpuinfo '^Model' | cut -d':' -f2 | cut -d' ' -f2-"\
            + "| awk '{print $1,$2,$3,$4}'"
        raspiModel = subprocess.check_output(cmd, shell=True).decode("utf-8")
        raspiModel = RASPI_ICON + raspiModel
        # Draw Raspi model.
        draw.text((x, y), raspiModel, font=smallFont, fill="white")
        y += smallFont.getsize(raspiModel)[1]

        # Get time
        cmd = "date '+%H:%M:%S' | tr -d '[:space:]'"
        timePresent = subprocess.check_output(cmd, shell=True).decode("utf-8")
        timePresent = CLOCK_ICON + timePresent
        # Draw time.
        x = (width / 2) - (largeFont.getsize(timePresent)[0] / 2)
        y += 5
        draw.text((x, y), timePresent, font=largeFont, fill="white")
        y += largeFont.getsize(timePresent)[1]

        # Get date.
        cmd = "date '+%Y/%m/%d' | tr -d '[:space:]'"
        dateToday = subprocess.check_output(cmd, shell=True).decode("utf-8")
        dateToday = CALENDER_ICON + dateToday
        # Draw date.
        x = (width / 2) - (defaultFont.getsize(dateToday)[0] / 2)
        y += 5
        draw.text((x, y), dateToday, font=defaultFont, fill="white")
        y += defaultFont.getsize(dateToday)[1]

        x = 0

        # Display imageBase.
        disp.image(baseImage)
        time.sleep(0.1)

except KeyboardInterrupt:
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    disp.image(baseImage)
    print('Keyboard interrupt.')
    exit()
