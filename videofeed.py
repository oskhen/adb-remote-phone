#!/usr/bin/env python3

import subprocess

command = "adb exec-out screenrecord --output-format=h264 - | ffplay -framerate 60 -probesize 32 -sync video -"

adb = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
output = adb.communicate()[0]
print(output)

# adb = subprocess.run(['adb', 'exec-out', 'screenrecord', '--output-format=h264', '-'], check=True, capture_output=True)

# ffplay = subprocess.run(['ffplay', '-framerate', '60', '-probesize', '32', '-sync', 'video', '-'], input=adb.stdout, capture_output=True)
