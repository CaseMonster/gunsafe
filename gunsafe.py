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
OPEN_TIME_MIN = 3
OPEN_TIME_MAX = 1000

#===========================================================================================
#functions
    
def TextCell():
    message = "GUNSAFE OPEN"

    try:
        smtpObj = smtplib.SMTP('smtp.gmail.com',587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
        smtpObj.login('cschneberger.gunsafe@gmail.com', 'kjowzkcawjavtdue')
        smtpObj.sendmail("cschneberger.gunsafe@gmail.com", "4056948973@txt.att.net", message)
        smtpObj.quit()
    except:
        print "error sending email"

def Log():
    t = str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    s = str(t + "\tSAFE_OPEN:" + str(SAFE_OPEN) + "\tOPEN_TIME: " + str(OPEN_TIME) + "\tTIMER:" + str(TIMER))
    print(s)

#===========================================================================================
#main

GPIO.output(LIGHTS_OUTSIDE, GPIO.HIGH)

while True:

    if GPIO.input(SENSOR):
        OPEN_TIME = OPEN_TIME + 1
        if OPEN_TIME > OPEN_TIME_MIN:
            if SAFE_OPEN == False:
                print "safe opened"
                SAFE_OPEN = True
                Log()
                print "turning on lights"
                GPIO.output(LIGHTS_INSIDE, GPIO.HIGH)
                print "email sent"
                TextCell()
            
    if not GPIO.input(SENSOR):
        if SAFE_OPEN == True:
            print "safe closed"
            print "turning off lights"
            GPIO.output(LIGHTS_INSIDE, GPIO.LOW)
        SAFE_OPEN = False
        OPEN_TIME = 0
        
    if SAFE_OPEN == True:
        if OPEN_TIME > OPEN_TIME_MAX:
            print "door opened for too long"
            SAFE_OPEN = False
            print "turning off lights"
            GPIO.output(LIGHTS_INSIDE, GPIO.LOW)
            OPEN_TIME = 0

    TIMER = TIMER + 1
    if (TIMER % 100) == 0:
        Log()
    if (TIMER % 1000) == 0:
        t = datetime.datetime.now()
        if ((int(t.hour) - 5) % 24) > 6:
            print "daytime"
            GPIO.output(LIGHTS_OUTSIDE, GPIO.HIGH)
        if ((int(t.hour) - 5) % 24) < 7:
            print "nighttime"
            GPIO.output(LIGHTS_OUTSIDE, GPIO.LOW)

    time.sleep(.25)
