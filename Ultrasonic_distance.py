# -*- coding: utf-8 -*-

#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO_BUZZ = 10      #buzzer
GPIO_SERVO = 16     #dispenser motor

 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_BUZZ, GPIO.OUT)
GPIO.setup(GPIO_SERVO, GPIO.OUT)
GPIO.setwarnings(False)
pwm = GPIO.PWM(GPIO_SERVO, 1000)

 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
def Dispenser(distance):        #Distance = distance read from sonar, inp = dispense command
    present = 10.0      #Fixed distance of cup
    d = distance
    if d < present:
        pwm.start(50)     #complete revolutions at fixed speed for 3 secs
        print "Container Present, Dispensing"
        time.sleep(3)
        pwm.stop()
        return
    
    else:
        print "Container not present"
        GPIO.output(GPIO_BUZZ, GPIO.HIGH)       #Buzzer Sounds
        time.sleep(0.5)
        GPIO.output(GPIO_BUZZ, GPIO.LOW)        #Buzzer off
        return

if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            Dispenser(dist)
            print ("Measured Distance = %.1f cm" % dist)
            time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
