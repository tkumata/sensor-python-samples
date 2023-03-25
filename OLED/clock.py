import os
import time
import subprocess

import board
import digitalio
from adafruit_rgb_display import ssd1351
from PIL import Image, ImageDraw, ImageFont

import little_strings as STR

print('Initializing PINs with digitalio library...')
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

print('Calling SPI...')
spi = board.SPI()

print('Calling text wrapper class...')
tw = STR.TextWrapper()

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

MAXWIDTH = width

print('Creating a black image...')
baseImage = Image.new("RGB", (width, height))
drawedBaseImage = ImageDraw.Draw(baseImage)
drawedBaseImage.rectangle((0, 0, width, height), outline=0, fill=0)
draw = ImageDraw.Draw(baseImage)

# First define some constants to allow easy positioning of text.
padding = -2

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
    28
)
hugeFont = ImageFont.truetype(
    os.path.dirname(__file__) +
    "/materials/SFMono-Regular-Nerd-Font-Complete.otf",
    34
)

DIST_ICON = u'\ufaca '
DESK_ICON = u'\ufb5a '
CLOCK_ICON = u'\ue38b '
TEMP_ICON = u'\uf2c9 '
CPU_ICON = u'\ue266 '
RASPI_ICON = u'\uf315'
CALENDER_ICON = u'\uf073 '


class LinuxCommands:
    def getPiModel(self):
        cmd = "grep </proc/cpuinfo '^Model' | cut -d':' -f2 | cut -d' ' -f2-"\
            + "| awk '{print $1, $2, $3, $4}'"
        raspiModel = subprocess.check_output(cmd, shell=True).decode("utf-8")
        raspiModel = raspiModel
        return raspiModel

    def getToday(self):
        cmd = "date '+%Y/%m/%d' | tr -d '[:space:]'"
        dateToday = subprocess.check_output(cmd, shell=True).decode("utf-8")
        dateToday = CALENDER_ICON + dateToday
        return dateToday

    def getTime(self):
        cmd = "date '+%H:%M' | tr -d '[:space:]'"
        now = subprocess.check_output(cmd, shell=True).decode("utf-8")
        now = CLOCK_ICON + now
        return now

    def getCpuInfo(self):
        # temparature
        cmd = "cat /sys/class/thermal/thermal_zone0/temp"\
            + " | awk '{printf \"%.1fC\", $(NF-0) / 1000}'"
        cpuInfo = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cpuInfo = CPU_ICON + cpuInfo
        # load average
        cmd = "top -bn1 | grep load | awk '{printf \"%.2f\", $(NF-2)}'"
        cpuLoad = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cpuInfo = cpuInfo + '/' + cpuLoad
        return cpuInfo


def fw_wrap(text, width=MAXWIDTH, **kwargs):
    w = STR.TextWrapper(width=width, **kwargs)
    return w.wrap(text)


def displayText(x, y, Text, font, cr=18):
    lines = fw_wrap(Text, cr)
    line_counter = 0

    for line in lines:
        y = y + line_counter * font.getsize(Text)[1]
        line_color = (255, 255, 255)

        # if line_counter % 2 != 0:
        #     line_color = (220, 220, 220)

        draw.multiline_text((x, y), line, fill=line_color, font=font)
        line_counter = line_counter + 1

    return line_counter


linuxCommands = LinuxCommands()

try:
    while True:
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Draw Pi logo at top right on display
        x = width - hugeFont.getsize(RASPI_ICON)[0]
        draw.text((x, 0), RASPI_ICON, font=hugeFont, fill="pink")
        logoEndY = hugeFont.getsize(RASPI_ICON)[1]

        x = 0
        y = padding

        # Draw Raspi model.
        piModel = linuxCommands.getPiModel()
        lineCounter = displayText(x, y, piModel, smallFont, 14)
        piModelY = smallFont.getsize(piModel)[1] * lineCounter

        if piModelY > logoEndY:
            y = piModelY
        else:
            y = logoEndY

        # Draw time.
        timeNow = linuxCommands.getTime()
        lineCounter = displayText(x, y, timeNow, largeFont)
        y += largeFont.getsize(timeNow)[1] * lineCounter

        # Draw date.
        dateToday = linuxCommands.getToday()
        lineCounter = displayText(x, y, dateToday, defaultFont)
        y += defaultFont.getsize(dateToday)[1] * lineCounter

        # Draw CPU info
        cpuInfo = linuxCommands.getCpuInfo()
        displayText(x, y, cpuInfo, defaultFont)

        # Display to baseImage.
        disp.image(baseImage)
        time.sleep(5)

except KeyboardInterrupt:
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    disp.image(baseImage)
    print('Keyboard interrupt.')
    exit()
