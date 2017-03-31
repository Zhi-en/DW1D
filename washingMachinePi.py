#Outline of Washing Machine Pi code
from firebase import getState
from firebase import putState

machineNum = 1

#main code you can either use state machine or a series of if statements
#if door open, red light offs, green light ons
#if button press for door close, red light on, green light offs, send: door closed
#if start wash, ensures red light on and green light is off (or in the door closed state), amber light ons
#if button press for wash finished, ensures amber light is on (or in washing state), switches amber light off and send: wash finished

#Enze's code
import RPi.GPIO as GPIO

import libdw.sm as sm

GPIO.setmode(GPIO.BCM)

led = [23,24,25]#23 FOR RED, 24 FOR GREEN, 25 FOR YELLOW
off = 18
lock = 19
start = 20

GPIO.setup(led, GPIO.OUT)
GPIO.setup(off, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(lock, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(start, GPIO.IN, GPIO.PUD_DOWN)

class Led(sm.SM):
    
    startState = -2
    
    def getNextValues(self, state, inp):
        is_off = GPIO.input(off) == GPIO.HIGH
        is_locked = GPIO.input(lock) == GPIO.HIGH
        is_unlocked = GPIO.input(lock) == GPIO.LOW
        is_started = GPIO.input(start) == GPIO.HIGH
        

        if state == -2:
            if inp == is_off:
                nextState = -1
                output = None
            else:
                pass
        if state == -1:
            if inp == is_locked:
                nextState = 0
                output = GPIO.output(led[0], GPIO.HIGH)
            else:
                pass
        if state == 0:
            if inp == is_started:
                nextState = 1
                output = GPIO.output(led[2], GPIO.HIGH),GPIO.output(led[0], GPIO.LOW)
                
            else:
                pass
        if state == 1:
            if inp == is_unlocked:
                nextState = 2
                output = GPIO.output(led[1], GPIO.HIGH),GPIO.output(led[2], GPIO.LOW)
                
            else:
                pass
        if state == 2:
            pass
