#!/usr/bin/pythonimport
import RPi.GPIO as GPIO
import sys

def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    print "Bye!"
    sys.exit()