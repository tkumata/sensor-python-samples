# Raspberry Pi Zero WH and HC-SR04 and SSD 1351
## これは何？
### SSD1351.py
自分と HC-SR04 との距離を測り特定距離なら自分が存在するとみなして Slack のステータスを変化させる python スクリプト。ついでに OLED に日付やラズパイの CPU 温度やセンサ距離などを表示させる。

## 必要なもの
* Grove な HC-SR04
* SSD 1351 な OLED モジュール
* 4 pin コネクタ - ジャンパピン
* ジャンパピン メス-メス
* materials ディレクトリ
  * GenShinGothic-Normal.ttf
* config.json
  * Slack app token
  * Slack member_id


## PINOUT
```shell
$ piout
.-------------------------.
| oooooooooooooooooooo J8 |
| 1ooooooooooooooooooo   |c
---+       +---+ PiZero W|s
 sd|       |SoC|   V1.1  |i
---+|hdmi| +---+  usb pwr |
`---|    |--------| |-| |-'

Revision           : 9000c1
SoC                : BCM2835
RAM                : 512MB
Storage            : MicroSD
USB ports          : 1 (of which 0 USB3)
Ethernet ports     : 0 (0Mbps max. speed)
Wi-fi              : True
Bluetooth          : True
Camera ports (CSI) : 1
Display ports (DSI): 0

J8:
   3V3  (1) (2)  5V
 GPIO2  (3) (4)  5V
 GPIO3  (5) (6)  GND
 GPIO4  (7) (8)  GPIO14
   GND  (9) (10) GPIO15
GPIO17 (11) (12) GPIO18
GPIO27 (13) (14) GND
GPIO22 (15) (16) GPIO23
   3V3 (17) (18) GPIO24
GPIO10 (19) (20) GND
 GPIO9 (21) (22) GPIO25
GPIO11 (23) (24) GPIO8
   GND (25) (26) GPIO7
 GPIO0 (27) (28) GPIO1
 GPIO5 (29) (30) GND
 GPIO6 (31) (32) GPIO12
GPIO13 (33) (34) GND
GPIO19 (35) (36) GPIO16
GPIO26 (37) (38) GPIO20
   GND (39) (40) GPIO21

For further information, please refer to https://pinout.xyz/
```

## Grove HC-SR04 v2.0 (Grove 超音波測距センサー)
HC-SR04 は 5v 入力の 5v 出力なので GPIO には 3v で渡さないといけない。ミニブレッドボードに抵抗を挿して云々をしたくなかったので Grove な HC-SR04 を GPIO に接続。

![画像](https://media-cdn.seeedstudio.com/media/catalog/product/cache/b5e839932a12c6938f4f9ff16fa3726a/g/r/grove---ultrasonic-distance-sensor-preview_1.png)

https://jp.seeedstudio.com/Grove-Ultrasonic-Distance-Sensor.html

### GPIO
* 5V5<br>
* GND<br>
* GPIO17 as SIG<br>


## Waveshare 14747 1.5inch RGB OLED Module
Chipset: SSD 1351

この商品は 3v in 3v out なので GPIO に直で接続できるので初心者は嬉しい。

![画像](https://www.welectron.com/media/image/product/11237/md/waveshare-14747-15inch-rgb-oled-module_1.jpg)

### Waveshare samples
https://www.welectron.com/Waveshare-14747-15inch-RGB-OLED-Module_1

### Adafruit SSD 1351 Samples
https://learn.adafruit.com/adafruit-1-5-color-oled-breakout-board/python-usage

### GPIO
* 3V3<br>
* GND<br>
* GPIO8  as CS<br>
* GPIO10 as MISO<br>
* GPIO11 as SCLK<br>
* GPIO24 as Reset<br>
* GPIO25 as DC<br>
