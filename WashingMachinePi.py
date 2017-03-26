#Outline of Washing Machine Pi code
from firebase import getState
from firebase import putState

machineNum = 1

#main code you can either use state machine or a series of if statements
#if door open, red light offs, green light ons
#if button press for door close, red light on, green light offs, send: door closed
#if start wash, ensures red light on and green light is off (or in the door closed state), amber light ons
#if button press for wash finished, ensures amber light is on (or in washing state), switches amber light off and send: wash finished