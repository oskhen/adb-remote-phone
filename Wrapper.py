import subprocess
import argparse


def main(config):
    screenrecording = subprocess.Popen(["adb", "exec-out", "screenrecord", "--output-format=h264", "-"], stdout=subprocess.PIPE)

    OpenCV = subprocess.run([config.python, "OpenCV.py", "-adb", config.PATH, "-m", config.Margin], stdin=screenrecording.stdout)
    


def initParser():
    parser = argparse.ArgumentParser(description="Control your Android phone remotely through a USB connection.")
    parser.add_argument("-adb", "--adb-path", action="store", type=str, dest="PATH", help="Path to ADB. Defaults to adb", default="adb")
    parser.add_argument("-m", "--margin", action="store", type=str, dest="Margin", help="Height margin in percentage of screen utilised. Defaults to 0.9", default="0.9")
    parser.add_argument("-p", "--python", action="store", type=str, dest="python", help="Path to python. Defaults to python3", default="python3")

    return parser


if __name__ == "__main__":
    parser = initParser()
    config = parser.parse_args()
    main(config)

    