#===========================================================================================
#init

import RPi.GPIO as GPIO
import time
import datetime
import os
import random
import smtplib

#os.system("modprobe w1-gpio")
#os.system("modprobe w1-therm")
#temp_sensor = "/sys/bus/w1/devices/28-0416239f59ff/w1_slave"

#===========================================================================================
#pin setup

LIGHTS_INSIDE = 38
LIGHTS_OUTSIDE_M = 40 
LIGHTS_OUTSIDE_1 = 29
LIGHTS_OUTSIDE_2 = 31
LIGHTS_OUTSIDE_3 = 33
LIGHTS_OUTSIDE_4 = 35
LIGHTS_OUTSIDE_5 = 37
MOTION_SENSOR = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LIGHTS_INSIDE, GPIO.OUT)
GPIO.setup(LIGHTS_OUTSIDE_M, GPIO.OUT)
GPIO.setup(LIGHTS_OUTSIDE_1, GPIO.OUT)
GPIO.setup(LIGHTS_OUTSIDE_2, GPIO.OUT)
GPIO.setup(LIGHTS_OUTSIDE_3, GPIO.OUT)
GPIO.setup(LIGHTS_OUTSIDE_4, GPIO.OUT)
GPIO.setup(LIGHTS_OUTSIDE_5, GPIO.OUT)
GPIO.setup(MOTION_SENSOR, GPIO.IN)

#===========================================================================================
#vars

SAFE_OPEN = False
TIMER = 0
MOTION_DETECTED = True
OPEN_TIME = 0
OPEN_TIME_MAX = 60

LIGHTS_OUTSIDE = [LIGHTS_OUTSIDE_1,LIGHTS_OUTSIDE_2,LIGHTS_OUTSIDE_3,LIGHTS_OUTSIDE_4,LIGHTS_OUTSIDE_5]
LIGHTS_OUTSIDE_ON = [True,True,True,True,True]

#===========================================================================================
#functions

def CheckMotion():
    if GPIO.input(MOTION_SENSOR):
        return True
    else:
        return False

def LightsInsideOn():
    GPIO.output(LIGHTS_INSIDE, GPIO.HIGH)

def LightsInsideOff():
    GPIO.output(LIGHTS_INSIDE, GPIO.LOW)

def LightsOutsideCycle():
    global LIGHTS_OUTSIDE
    global LIGHTS_OUTSIDE_ON
    for index, light in enumerate(LIGHTS_OUTSIDE):
        if LIGHTS_OUTSIDE_ON[index] == True:
            GPIO.output(LIGHTS_OUTSIDE[index], GPIO.HIGH)
        else:
            GPIO.output(LIGHTS_OUTSIDE[index], GPIO.LOW)

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

while True:

    if CheckMotion():
        print("motion detected")
        if SAFE_OPEN == False:
            print("sending text")
            #TextCell()
        SAFE_OPEN = True
        LightsInsideOn()
        OPEN_TIME = 0

    if SAFE_OPEN:
        OPEN_TIME = OPEN_TIME + 1
        if OPEN_TIME > OPEN_TIME_MAX:
            print("lights out")
            SAFE_OPEN = False
            LightsInsideOff()
            OPEN_TIME = 0

    if TIMER % 60 == 0:
        print("cycling outside lights")
        TIMER = 0
        LightsOutsideCycle()

    Log()
    TIMER = TIMER + 1
    time.sleep(1)
    
    
