#!/usr/bin/env python2

# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:si:et:enc=utf-8

import sys, serial, struct, os, time

DEBUG = False

def dprint(data):
    if DEBUG:
        print(data)

port = sys.argv[1]
dprint("Connecting with " + port)

try:
    sp = serial.Serial(
        port=port,
        baudrate=115200,     # baudrate
        bytesize=8,             # number of databits
        stopbits=1,
        xonxoff=0,              # don't enable software flow control
        rtscts=0,               # don't enable RTS/CTS flow control
        timeout=3               # set a timeout value, None for waiting forever
    )
except serial.SerialException:
    dprint("Connection error, check serial")
    print("ERROR: ESERIALCONN")
    sys.exit(0)

k = "\xff\xff\xffconnect\xff\xff\xff\xff\xff\xffconnect\xff\xff\xff"
sp.write(k)

str = sp.read(10).strip("\xff\x00")

dprint("Received: " + str)
if len(str) == 0 or str.find("comok") == -1:
    dprint("Serial communication error, check serial")
    dprint("Received Strlen: " + repr(len(str)))
    print("ERROR: ESERIALCOMM")
    sys.exit(0)
    
update = open("update.tft", "rb")
updateSize = os.path.getsize("update.tft")
dprint("Update size is " + updateSize.__str__())

sp.write("\xff\xff\xffwhmi-wri " + updateSize.__str__() + ",115200,0\xff\xff\xff")
sp.write("\xff\xff\xffwhmi-wri " + updateSize.__str__() + ",115200,0\xff\xff\xff")
# I don't know why but I have to write this line two times to make it work...

c = " "
while c != "\x05":
    c = sp.read(1)
    dprint("Received: " + repr(c))
    if len(c) == 0:
        dprint("Serial connection broke, check serial")
        print("ERROR: ESERIALBROKE")
        sys.exit(0)

dprint("Start Flash")
dataBits = " "
i = 0

lastTime = time.time()
while len(dataBits) != 0:
    dataBits = update.read(4096)
    if len(dataBits) == 0:
        print("Write OK")
        sys.exit(0)

    dprint("Writing " + repr(len(dataBits)) + " bytes")
    sp.write(dataBits)

    c = " "
    while c != "\x05":
        c = sp.read(1)
        dprint("Received: " + repr(c))
        if len(c) == 0:
            dprint("Serial connection broke, check serial")
            print("ERROR: ESERIALBROKE")
            sys.exit(0)
            
    i += 1
    if i % 3 == 0:
        print("<1>" + repr((i + 1) * 4096) + "<2>" + repr(int(4096 * 3 / (time.time() - lastTime))) + "<3>" + port + "<4>")
        lastTime = time.time()
    
    
