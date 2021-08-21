#from os import path
import cv2
import sys
#import numpy as np
import subprocess
#import math
import re
from screeninfo import get_monitors
import argparse
import time
from timeit import default_timer

# TODO: 
# Change duration timings?
# fix delays (onClick every time mouse is moved in window!)
# Requires USB Debugging?
# Fix internal piping

startTime, startX, startY = [0]*3

def initADB():
    global path
    output = str(subprocess.run([path, "devices"], capture_output=True).stdout).split("\\n")
    devices = [x for x in output if "\\t" in x]
    if not devices:
        print("No devices attached. Check your USB connection and try again")
        exit()
    elif len(devices) > 1:
        print("More than one device attached. Disconnect other connected devices and try again")
        exit()
    else:
        device = devices[0].split("\\t")[0]
        print(f"Device with ID {device} found.")


def getResolution():
    global path
    output = str(subprocess.run([path, "exec-out", "wm", "size"], capture_output=True).stdout).split("\\n")[0]
    width, height = map(int, re.sub(r'[^0-9x]', '', output).split("x"))
    return width, height

def initParser():
    parser = argparse.ArgumentParser(description="Control your Android phone remotely through a USB connection.")
    parser.add_argument("-adb", "--adb-path", action="store", type=str, dest="PATH", help="Path to ADB. Defaults to adb", default="adb")
    parser.add_argument("-m", "--margin", action="store", type=float, dest="Margin", help="Height margin in percentage of screen utilised. Defaults to 0.9", default=0.9)

    return parser

def swipe(x1, y1, x2, y2, duration):
    duration = int((duration*1000))
    print(f"swipe {x1} {y1} {x2} {y2} {duration}")
    subprocess.run([path, "exec-out", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

def touch(x, y):
    print(f"touch event at {x}, {y}")
    subprocess.run([path, "exec-out", "input", "tap", str(x), str(y)])    

def onClick(event, x, y, flags, param):
    global startTime
    global startX
    global startY

    if (event == cv2.EVENT_LBUTTONDOWN):

        startTime = default_timer()
        startX = x
        startY = y

    elif (event == cv2.EVENT_LBUTTONUP):

        time = default_timer() - startTime

        if startX == x and startY == y:
            touch(x, y)
        else:
            swipe(startX, startY, x, y, time)


def main(config):
    global path

    #|- Config
    marginFactor = config.Margin
    path = config.PATH
    #|--

    initADB()

    #- Resize calculations
    phoneWidth, phoneHeight = getResolution()
    displayHeight = get_monitors()[0].height
    displayHeight = round(displayHeight*marginFactor)
    scaling = displayHeight / phoneHeight
    displayWidth = round(phoneWidth * scaling)
    #|----------


    print(f"Phone resolution: {phoneWidth}x{phoneHeight}")
    print(f"Converting to display resolution: {displayWidth}x{displayHeight}")

    cap = cv2.VideoCapture("/dev/stdin")

    if (cap.isOpened()==False):
        print("Failed to open stream")

    cv2.namedWindow("main", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("main", displayWidth, displayHeight)
    cv2.setMouseCallback("main", onClick)

    while cap.isOpened():

        ret, frame = cap.read()
        if ret == True:

            cv2.imshow('main', frame)
            
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        
        else:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = initParser()
    config = parser.parse_args()
    main(config)