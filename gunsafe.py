#===========================================================================================
#init

import RPi.GPIO as GPIO
import time
import datetime
import os
import random
import smtplib

GPIO.setwarnings(False)

#===========================================================================================
#pin setup

SENSOR = 40
LIGHTS_OUTSIDE = 36
LIGHTS_INSIDE = 38

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LIGHTS_OUTSIDE, GPIO.OUT)
GPIO.setup(LIGHTS_INSIDE, GPIO.OUT)
GPIO.setup(SENSOR, GPIO.IN)

#===========================================================================================
#vars

SAFE_OPEN = False
TIMER = 0
OPEN_TIME = 0
OPEN_TIME_MAX = 10

#===========================================================================================
#functions

def CheckSensor():
    return False  #broken sensor work around
    if GPIO.input(SENSOR):
        return True
    else:
        return False
    
def TextCell():
    message = "MSG: GUNSAFE OPEN" + str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

    try:
        smtpObj = smtplib.SMTP('smtp.gmail.com',587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login('cschneberger.gunsafe@gmail.com', 'kjowzkcawjavtdue')
        smtpObj.sendmail('cschneberger.gunsafe@gmail.com', '4056948973@txt.att.net', message)
        smtpObj.quit()
        print "email sent"
    except:
        print "error on sending email"

def Log():
    t = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    s = str(t + "\tSAFE_OPEN:" + str(SAFE_OPEN) + "\tOPEN_TIME: " + str(OPEN_TIME) + "\tTIMER:" + str(TIMER))
    print(s)

#===========================================================================================
#main

GPIO.output(LIGHTS_OUTSIDE, GPIO.HIGH)

while True:

    if CheckSensor():
        print("door open detected")
        OPEN_TIME = 0
        if SAFE_OPEN == False:
            print("sending text")
            #TextCell()
            SAFE_OPEN = True
            GPIO.output(LIGHTS_INSIDE, GPIO.HIGH)

    if SAFE_OPEN:
        OPEN_TIME = OPEN_TIME + 1
        if OPEN_TIME > OPEN_TIME_MAX:
            print("lights out")
            SAFE_OPEN = False
            GPIO.output(LIGHTS_INSIDE, GPIO.LOW)
            OPEN_TIME = 0

    TIMER = TIMER + 1
    if (TIMER % 100):
        Log()
    if (TIMER % 1000):
        t = datetime.datetime.now()
        if ((int(t.hour) - 6) % 24) > 6:
            GPIO.output(LIGHTS_OUTSIDE, GPIO.HIGH)
        if ((int(t.hour) - 6) % 24) < 7:
            GPIO.output(LIGHTS_OUTSIDE, GPIO.LOW)

    time.sleep(.25)
