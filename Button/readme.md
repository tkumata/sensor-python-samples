# Raspberry Pi 3B and Grove Button
3B+ じゃなくて 3B

## これは何？
### punch_in_out.py
ボタンを押したら Slack の特定チャンネルに投稿する python スクリプト。

- 一回押下で仕事始めるメッセージを投稿
- 二回素早く押下(ダブルクリック的な押下)で離席を表すメッセージを投稿
- 長押しで業務終了を表すメッセージを投稿

### Button.py
上記の試作。

## 必要なもの
* Grove な Button モジュール
* 4 pin コネクタをジャンパピンに変えるケーブル
* ジャンパピン メス-メス 4本
* config.json
  * Slack app token
  * Slack member_id
  * Slack channel id

## PINOUT
```shell
$ pinout
,--------------------------------.
| oooooooooooooooooooo J8     +====
| 1ooooooooooooooooooo        | USB
|                             +====
|      Pi Model 3B  V1.2         |
|      +----+                 +====
| |D|  |SoC |                 | USB
| |S|  |    |                 +====
| |I|  +----+                    |
|                   |C|     +======
|                   |S|     |   Net
| pwr        |HDMI| |I||A|  +======
`-| |--------|    |----|V|-------'

Revision           : a32082
SoC                : BCM2837
RAM                : 1GB
Storage            : MicroSD
USB ports          : 4 (of which 0 USB3)
Ethernet ports     : 1 (100Mbps max. speed)
Wi-fi              : True
Bluetooth          : True
Camera ports (CSI) : 1
Display ports (DSI): 1

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

## Grove Button
![画像](https://cdn.shopify.com/s/files/1/0514/0719/2262/products/3f75a3fb-2ef5-4761-a5ca-6ca068af190a_e95a2aa2-4da8-4b78-96c3-0c95ca2c5ac4_500x500.jpg?v=1675274666)

### GPIO
3V3<br>
GND<br>
GPIO15 as SIG<br>
