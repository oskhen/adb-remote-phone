import cv2
import sys
import numpy as np
import subprocess
import math
import re
from screeninfo import get_monitors

# TODO: 
# x/y scaling is off
# auto-display resolution
# initADB (is it needed?)
# adb path
# swipe
# fix delays (onClick every time mouse is moved in window!)

# adb shell settings put system show_touches 1

def initADB():
    pass

def getResolution():
    output = str(subprocess.run(["adb", "exec-out", "wm", "size"], capture_output=True).stdout).split("\\n")[0]
    width, height = map(int, re.sub(r'[^0-9x]', '', output).split("x"))
    return width, height
    

#- Config
marginFactor = 0.9

displayHeight = 1080

#|---------

#- Resize calculations
phoneWidth, phoneHeight = getResolution()
displayHeight = round(displayHeight*marginFactor)
scaling = displayHeight / phoneHeight
displayWidth = round(phoneWidth * scaling)
#|----------

def onClick(event, x, y, flags, param):

    if (event == cv2.EVENT_LBUTTONDOWN):

        print(f"touch event at {x}, {y}")
        subprocess.run(["adb", "exec-out", "input", "tap", str(x), str(y)])







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
exit()