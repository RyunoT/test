#!/usr/bin/env python
#
# WINSTAR OLED 16x2 CHARACTER DISPLAY
# +----+-----+--------------------|
# | No | Pin | Desc               |
# +----+-----+--------------------|
# |  1 | VSS | GND                |
# |  2 | VDD | 3.3V or 5V         |
# |  3 | NC  | Not Used           |
# |  4 | RS  | 0: Command 1: Data |
# |  5 | RW  | 0: Write   1: Read |
# |  6 | E   | Enable             |
# |  7 | D0  | Data bit 0         |
# |  8 | D1  | Data bit 1         |
# |  9 | D2  | Data bit 2         |
# | 10 | D3  | Data bit 3         |
# | 11 | D4  | Data bit 4         |
# | 12 | D5  | Data bit 5         |
# | 13 | D6  | Data bit 6         |
# | 14 | D7  | Data bit 7         |
# | 15 | NC  | Not Used           |
# | 16 | NC  | Not Used           |
# +----+-----+--------------------|




import RPi.GPIO as GPIO
import time
import subprocess

RS = 7
E = 8
D4 = 25
D5 = 24
D6 = 23
D7 = 18

DATA = True
COMMAND = False


def main():
    i = 0

    setup()

    while True:

        vmstatout = subprocess.check_output(["vmstat"])
        cpuidle = int(vmstatout[233:236])
        cpubusy = 100 - cpuidle

        lcdSetPos(0, 0)
        lcdPutStr("CPU{:>3d}%".format(cpubusy))

        lcdSetPos(1, 0)
        memfree = int(vmstatout[174:181])
        lcdPutStr("FREE{:7d}KB".format(memfree))

        lcdSetPos(1, 15)
        if i == 0:
            lcdPutStr("-")
        if i == 1:
            lcdPutStr("*")
        if i == 2:
            lcdPutStr("|")
        if i == 3:
            lcdPutStr("*")
            i += 1
        if i > 3:
            i = 0

        time.sleep(1)


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(E, GPIO.OUT)
    GPIO.setup(RS, GPIO.OUT)
    GPIO.setup(D4, GPIO.OUT)
    GPIO.setup(D5, GPIO.OUT)
    GPIO.setup(D6, GPIO.OUT)
    GPIO.setup(D7, GPIO.OUT)

    time.sleep(0.05)
    lcdPut4bit(0x03)
    time.sleep(0.05)
    lcdPut4bit(0x08)
    time.sleep(0.05)
    lcdPut4bit(0x02)
    time.sleep(0.05)
    lcdPut4bit(0x02)
    time.sleep(0.05)
    lcdPut4bit(0x08)
    time.sleep(0.05)
    lcdPutByte(0x08, COMMAND)
    time.sleep(0.05)
    lcdPutByte(0x01, COMMAND)
    time.sleep(0.05)
    lcdPutByte(0x06, COMMAND)
    time.sleep(0.05)
    lcdPutByte(0x02, COMMAND)
    time.sleep(0.05)
    lcdPutByte(0x0c, COMMAND)
    time.sleep(0.05)


def lcdPutByte(byte, mode):
    GPIO.output(RS, mode)
    time.sleep(0.01)
    GPIO.output(D4, GPIO.LOW)
    GPIO.output(D5, GPIO.LOW)
    GPIO.output(D6, GPIO.LOW)
    GPIO.output(D7, GPIO.LOW)

    if byte & 0x10 == 0x10:
        GPIO.output(D4, GPIO.HIGH)
    if byte & 0x20 == 0x20:
        GPIO.output(D5, GPIO.HIGH)
    if byte & 0x40 == 0x40:
        GPIO.output(D6, GPIO.HIGH)
    if byte & 0x80 == 0x80:
        GPIO.output(D7, GPIO.HIGH)

    lcdE()

    GPIO.output(D4, GPIO.LOW)
    GPIO.output(D5, GPIO.LOW)
    GPIO.output(D6, GPIO.LOW)
    GPIO.output(D7, GPIO.LOW)

    if byte & 0x01 == 0x01:
        GPIO.output(D4, GPIO.HIGH)
    if byte & 0x02 == 0x02:
        GPIO.output(D5, GPIO.HIGH)
    if byte & 0x04 == 0x04:
        GPIO.output(D6, GPIO.HIGH)
    if byte & 0x08 == 0x08:
        GPIO.output(D7, GPIO.HIGH)

    lcdE()


def lcdPut4bit(byte):
    GPIO.output(RS, GPIO.LOW)
    time.sleep(0.0001)
    GPIO.output(D4, GPIO.LOW)
    GPIO.output(D5, GPIO.LOW)
    GPIO.output(D6, GPIO.LOW)
    GPIO.output(D7, GPIO.LOW)

    if byte & 0x01 == 0x01:
        GPIO.output(D4, GPIO.HIGH)
    if byte & 0x02 == 0x02:
        GPIO.output(D5, GPIO.HIGH)
    if byte & 0x04 == 0x04:
        GPIO.output(D6, GPIO.HIGH)
    if byte & 0x08 == 0x08:
        GPIO.output(D7, GPIO.HIGH)

    lcdE()


def lcdE():
    time.sleep(0.01)
    GPIO.output(E, GPIO.HIGH)
    time.sleep(0.01)
    GPIO.output(E, GPIO.LOW)
    time.sleep(0.01)


def lcdSetPos(line, col):
    rowOffset = (0x80, 0xc0)
    lcdPutByte(rowOffset[line] | col, COMMAND)


def lcdPutStr(str):
    length = len(str)
    for i in range(length):
        lcdPutByte(ord(str[i]), DATA)


def lcdClear():
    lcdPutByte(0x01, COMMAND)


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcdClear()
        lcdSetPos(0, 0)
        lcdPutStr("Goodbye!")
        GPIO.cleanup()
