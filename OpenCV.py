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
import os
import threading

    
def isWindows():
    return(os.name == 'nt')

if isWindows():
    import win32pipe, win32file


# TODO: 
# Change duration timings?
# Requires USB Debugging?
# Fix internal piping

startTime, startX, startY = [0]*3

# https://stackoverflow.com/a/65191619
class VideoBufferCleanerThread(threading.Thread):
    def __init__(self, video, name='video-buffer-cleaner-thread'):
        self.video = video
        self.last_frame = None
        super(VideoBufferCleanerThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            threading.Lock()
            ret, self.last_frame = self.video.read()

# https://answers.opencv.org/question/28744/python-cv2videocapture-from-subprocesspipe/
def runPipe(PipePath):    
        p = win32pipe.CreateNamedPipe(PipePath,
                                        win32pipe.PIPE_ACCESS_DUPLEX,
                                        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
                                        1, 1024, 1024, 0, None)        
        win32pipe.ConnectNamedPipe(p, None)    
        while(True):
            data = sys.stdin.buffer.read(4096)
            if not data:
                break
            win32file.WriteFile(p,data)

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

    _thr = 0
    pipeName = "/dev/stdin"
    if(isWindows()):
        pipeName = r'\\.\\pipe\\myNamedPipe'
        _thr = threading.Thread(target=runPipe,args=[pipeName])
        _thr.start()

    cap = cv2.VideoCapture(pipeName)

    cap_cleaner = VideoBufferCleanerThread(cap)

    if (cap.isOpened()==False):
        print("Failed to open stream")

    cv2.namedWindow("main", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("main", displayWidth, displayHeight)
    cv2.setMouseCallback("main", onClick)

    while cap.isOpened():

        if cap_cleaner.last_frame is not None:

            threading.Lock()

            cv2.imshow('main', cap_cleaner.last_frame)
            
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = initParser()
    config = parser.parse_args()
    main(config)