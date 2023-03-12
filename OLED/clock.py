import os
import subprocess
# import time

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
RASPI_ICON = u'\uf315 '
CALENDER_ICON = u'\uf073 '


class LinuxCommands:
    def getPiModel(self):
        cmd = "grep </proc/cpuinfo '^Model' | cut -d':' -f2 | cut -d' ' -f2-"\
            + "| awk '{print $1,$2,$3,$4}'"
        raspiModel = subprocess.check_output(cmd, shell=True).decode("utf-8")
        raspiModel = RASPI_ICON + raspiModel
        return raspiModel

    def getToday(self):
        cmd = "date '+%Y/%m/%d' | tr -d '[:space:]'"
        dateToday = subprocess.check_output(cmd, shell=True).decode("utf-8")
        dateToday = CALENDER_ICON + dateToday
        return dateToday

    def getTime(self):
        cmd = "date '+%H:%M:%S' | tr -d '[:space:]'"
        timePresent = subprocess.check_output(cmd, shell=True).decode("utf-8")
        timePresent = CLOCK_ICON + timePresent
        return timePresent

    def getCpuInfo(self):
        cmd = "cat /sys/class/thermal/thermal_zone0/temp"\
            + " | awk '{printf \"%.1fC\", $(NF-0) / 1000}'"
        cpuInfo = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cpuInfo = CPU_ICON + cpuInfo

        cmd = "top -bn1 | grep load | awk '{printf \"%.2f\", $(NF-2)}'"
        cpuLoad = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cpuInfo = cpuInfo + ' / ' + cpuLoad

        return cpuInfo


linuxCommands = LinuxCommands()

try:
    while True:
        y = padding
        x = 0

        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Draw Raspi model.
        piModel = linuxCommands.getPiModel()
        draw.text((x, y), piModel, font=smallFont, fill="white")
        y += smallFont.getsize(piModel)[1] + 10

        # Draw time.
        timePresent = linuxCommands.getTime()
        draw.text((x, y), timePresent, font=largeFont, fill="white")
        y += largeFont.getsize(timePresent)[1] + 2

        # Draw date.
        dateToday = linuxCommands.getToday()
        x = (width / 2) - (defaultFont.getsize(dateToday)[0] / 2)
        draw.text((x, y), dateToday, font=defaultFont, fill="white")
        y += defaultFont.getsize(dateToday)[1] + 5

        # Draw CPU
        cpuInfo = linuxCommands.getCpuInfo()
        x = 0
        draw.text((x, y), cpuInfo, font=defaultFont, fill="white")

        # Display baseImage.
        disp.image(baseImage)
        # time.sleep(0.1)

except KeyboardInterrupt:
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    disp.image(baseImage)
    print('Keyboard interrupt.')
    exit()
