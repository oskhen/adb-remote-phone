import cv2
import sys
import numpy as np
import subprocess


cap = cv2.VideoCapture("/dev/stdin")

if (cap.isOpened()==False):
    print("Failed to open stream")


while cap.isOpened():
    ret, frame = cap.read()
    if ret == True:
        cv2.imshow('Frame', frame)
        
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    
    else:
        break
cap.release()
cv2.destroyAllWindows()
