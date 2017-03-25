#Outline of Washing Machine Pi code

#function that receives signal from main pi, returns instructions: door open, start wash, 
def receive():
    pass

#function that sends signal to main pi, inputs information: door closed, wash finished
def send(inp):
    pass

#main code you can either use state machine or a series of if statements
#if receives signal to door open, red light offs, green light ons
#if button press for door close, red light on, green light offs, send: door closed
#if receives signal for start wash, ensures red light on and green light is off (or in the door closed state), amber light ons
#if button press for wash finished, ensures amber light is on (or in washing state), switches amber light off and send: wash finished