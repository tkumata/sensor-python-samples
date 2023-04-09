#!/usr/bin/python3
# -*- coding: utf-8 -*-
from logging import getLogger, StreamHandler, DEBUG
import binascii
import nfc
import sys
import dbus
import keymap

HID_DBUS = 'org.yaptb.btkbservice'
HID_SRVC = '/org/yaptb/btkbservice'


logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False
logger.debug('hello timecard')


class MyCardReader(object):
    def on_connect(self, tag):
        if isinstance(tag, nfc.tag.tt3.Type3Tag):
            self.idm = binascii.hexlify(tag.idm)
            upperIDm = self.idm.upper()
            skc = SendKeycode()

            for char in upperIDm:
                skc.popinSendKey(char)

        return True

    def read_id(self):
        clf = nfc.ContactlessFrontend('usb')
        try:
            clf.connect(rdwr={'on-connect': self.on_connect})
        finally:
            clf.close()


class SendKeycode:
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.btkobject = self.bus.get_object(HID_DBUS, HID_SRVC)
        self.btk_service = dbus.Interface(self.btkobject, HID_DBUS)

    def popinSendKey(self, send_string):
        targetCode = int(keymap.keytable[send_string])
        targetKeys = [161, 1, 0, 0, targetCode, 0, 0, 0, 0, 0]
        all_keys_up = [161, 1, 0, 0, 0, 0, 0, 0, 0, 0]

        self.btk_service.send_keys(targetKeys)
        self.btk_service.send_keys(all_keys_up)


if __name__ == '__main__':
    try:
        cr = MyCardReader()

        while True:
            logger.debug("Please touch card.")
            cr.read_id()
            logger.debug("Card has released.")
    except KeyboardInterrupt:
        sys.exit()
    except IOError:
        logger.debug("Error: Pasori not found.")
