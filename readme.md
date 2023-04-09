# Raspberry Pi and sensors
# Setup
## Install packages

- sudo apt install libopenjp2-7 libtiff5
- sudo apt install fonts-dejavu-core
- sudo apt install libatlas-base-dev
- sudo apt install i2c-tools

## Install libraries

- sudo pip3 install adafruit-circuitpython-rgb-display
- sudo pip3 install adafruit-circuitpython-ssd1351
- sudo pip3 install adafruit-blinka
- sudo pip3 install pillow
- sudo pip3 install numpy
- sudo pip3 install RPi.GPIO
- sudo pip3 install smbus

#
Install neofetch
```
sudo apt install neofetch
```
Edit update-motd.d
```
sudo vi /etc/update-motd.d/90-neofetch
sudo chmod +x /etc/update-motd.d/90-neofetch
```
90-neofetch
```
#!/bin/sh
/usr/bin/neofetch
```
Result
```
  `.::///+:/-.        --///+//-:``    XXXXXX@XXXX
 `+oooooooooooo:   `+oooooooooooo:    -----------
  /oooo++//ooooo:  ooooo+//+ooooo.    OS: Raspbian GNU/Linux 11 (bullseye) armv7l
  `+ooooooo:-:oo-  +o+::/ooooooo:     Host: Raspberry Pi 3 Model B Rev 1.2
   `:oooooooo+``    `.oooooooo+-      Kernel: 5.15.61-v7+
     `:++ooo/.        :+ooo+/.`       Uptime: 1 hour, 11 mins
        ...`  `.----.` ``..           Packages: 643 (dpkg)
     .::::-``:::::::::.`-:::-`        Shell: bash 5.1.4
    -:::-`   .:::::::-`  `-:::-       Terminal: /dev/pts/0
   `::.  `.--.`  `` `.---.``.::`      CPU: BCM2835 (4) @ 1.200GHz
       .::::::::`  -::::::::` `       Memory: 523MiB / 922MiB
 .::` .:::::::::- `::::::::::``::.
-:::` ::::::::::.  ::::::::::.`:::-
::::  -::::::::.   `-::::::::  ::::
-::-   .-:::-.``....``.-::-.   -::-
 .. ``       .::::::::.     `..`..
   -:::-`   -::::::::::`  .:::::`
   :::::::` -::::::::::` :::::::.
   .:::::::  -::::::::. ::::::::
    `-:::::`   ..--.`   ::::::.
      `...`  `...--..`  `...`
            .::::::::::
             `.-::::-`
```

# Notes
```
sudo pip3 install pip-review
sudo pip-review --auto
```
