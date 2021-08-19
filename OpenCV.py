import cv2
import sys
import numpy as np
import subprocess
import math

marginFactor = 0.9

phoneWidth = 1440
phoneHeight = 2880

displayHeight = math.floor(1080*marginFactor)


displayWidth = math.floor(1440 * (displayHeight / phoneHeight))

print(f"Phone resolution: {phoneWidth}x{phoneHeight}")
print(f"Converting to display resolution: {displayWidth}x{displayHeight}")

cap = cv2.VideoCapture("/dev/stdin")

if (cap.isOpened()==False):
    print("Failed to open stream")

cv2.namedWindow("main", cv2.WINDOW_AUTOSIZE)

while cap.isOpened():

    ret, frame = cap.read()
    if ret == True:
        frame = cv2.resize(frame, (displayWidth, displayHeight))
        cv2.imshow('main', frame)
        
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    
    else:
        break

cap.release()
cv2.destroyAllWindows()
exit()