#!/usr/bin/env python3

import os
import unittest
import subprocess

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

CONVERT_THRESHOLD = "50%"
TESS_OPTS = "-psm 7"

# TODO - removed 5 because the 3s look more like 5s than 3s to tesseract
# I think we'll need to retrain to fix this. See:
#  https://github.com/tesseract-ocr/tesseract/wiki/TrainingTesseract
TESS_DIGITS_OPTS = TESS_OPTS + " -c tessedit_char_whitelist=012346789:"

def parseClockTime(clockTime):
    minutes, seconds = clockTime.strip().split(":")
    return int(minutes)*60 + int(seconds)

def parseMistakesStr(mistakesStr):
    if "none" in mistakesStr:
        return 0
    if "X" in mistakesStr:
        return mistakesStr.count('X')
    if "mistakes: 4 " in mistakesStr:
        return 4
    return mistakesStr

def parseScreenshot(path):
    parsed = {}

    # time
    p = subprocess.run("convert -crop 85x30+320+1050 -threshold {CONVERT_THRESHOLD} {path} - | tesseract {TESS_DIGITS_OPTS} stdin stdout digits".format(CONVERT_THRESHOLD=CONVERT_THRESHOLD, TESS_DIGITS_OPTS=TESS_DIGITS_OPTS, path=path), shell=True, check=True, stdout=subprocess.PIPE)
    clockTimeStr = p.stdout.decode('utf8')
    parsed["seconds"] = parseClockTime(clockTimeStr)

    # mistakes
    p = subprocess.run("convert -crop 519x40+200+360 -threshold {CONVERT_THRESHOLD} {path} - | tesseract {TESS_OPTS} stdin stdout".format(CONVERT_THRESHOLD=CONVERT_THRESHOLD, TESS_OPTS=TESS_OPTS, path=path), shell=True, check=True, stdout=subprocess.PIPE)
    mistakesStr = p.stdout.decode('utf8')
    parsed["mistakes"] = parseMistakesStr(mistakesStr)

    return parsed
    

class ParseTest(unittest.TestCase):
    pass

def generateTest(path):
    def test(self):
        level, secondsStr, mistakesStr = os.path.splitext(path)[0].split("_")
        seconds = int(secondsStr[:-1])
        mistakes = int(mistakesStr.split("m")[0])
        screenshot = {
            "path": path,
            "level": level,
            "seconds": seconds,
            "mistakes": mistakes,
        }

        parsed = parseScreenshot(screenshot['path'])
        self.assertEqual(parsed['seconds'], screenshot['seconds'])
        self.assertEqual(parsed['mistakes'], screenshot['mistakes'])
    return test

for f in os.listdir(TEST_DATA_DIR):
    path = os.path.join(TEST_DATA_DIR, f)
    setattr(ParseTest, "test_{}".format(f), generateTest(path))

if __name__ == "__main__":
    unittest.main()
