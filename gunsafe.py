#===========================================================================================
#init

import RPi.GPIO as GPIO
import pigpio
import time
import datetime
import os
import random
import smtplib

pwm = pigpio.pi()

GPIO.setwarnings(False)

#===========================================================================================
#pin setup

DOOR_SENSOR = 40

LInside = 38

LR = 35
LG = 12 #GPIO not pin number [32]
LB = 13 #GPIO not pin number [33]
LW = 37

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LInside, GPIO.OUT)
GPIO.setup(LR, GPIO.OUT)
#GPIO.setup(LG, GPIO.OUT)
#GPIO.setup(LB, GPIO.OUT)
GPIO.setup(LW, GPIO.OUT)
GPIO.setup(DOOR_SENSOR, GPIO.IN)

#LRpwm = GPIO.PWM(LR, 100)
#LGpwm = GPIO.PWM(LG, 100)
#LBpwm = GPIO.PWM(LB, 100)
#LWpwm = GPIO.PWM(LW, 100)


#===========================================================================================
#vars

SAFE_OPEN = False
TIMER = 0
OPEN_TIME = 0
OPEN_TIME_MAX = 10

CurrentColor = LG
CurrentMode = "Up"
Delta = 0


#===========================================================================================
#functions

def CheckSensor():
    if GPIO.input(DOOR_SENSOR):
        return True
    else:
        return False

def LightsInsideOn():
    GPIO.output(LInside, GPIO.HIGH)

def LightsInsideOff():
    GPIO.output(LInside, GPIO.LOW)

def LightsOutsideRed():
    pwm.hardware_PWM(LB, 500000, 0)
    pwm.hardware_PWM(LG, 500000, 0)
    
    GPIO.output(LR, GPIO.HIGH)

def LightsOutsideCycle():
    global CurrentColor
    global CurrentMode
    global Delta

    print(CurrentColor)
    print(Delta)

    GPIO.output(LR, GPIO.LOW)
    
    if CurrentColor == LG:
        if CurrentMode == "Up":
            Delta = Delta + 2500
            if (Delta % 500000) == 0:
                CurrentMode = "Down"
        elif CurrentMode == "Down":
            Delta = Delta - 2500
            if (Delta == 0):
                CurrentMode = "Up"
                CurrentColor = LB
        pwm.hardware_PWM(LG, 500000, Delta)

    elif CurrentColor == LB:
        if CurrentMode == "Up":
            Delta = Delta + 2500
            if (Delta % 500000) == 0:
                CurrentMode = "Down"
        elif CurrentMode == "Down":
            Delta = Delta - 2500
            if (Delta == 0):
                CurrentMode = "Up"
                CurrentColor = LG
        pwm.hardware_PWM(LB, 500000, Delta)


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

    if CheckSensor():
        print("door open detected")
        OPEN_TIME = 0
        if SAFE_OPEN == False:
            print("sending text")
            #TextCell()
            SAFE_OPEN = True
            LightsInsideOn()
            LightsOutsideRed()
            
    if SAFE_OPEN:
        OPEN_TIME = OPEN_TIME + 1
        if OPEN_TIME > OPEN_TIME_MAX:
            print("lights out")
            SAFE_OPEN = False
            LightsInsideOff()
            OPEN_TIME = 0

    if not SAFE_OPEN:      
        LightsOutsideCycle()
            
    #TIMER = TIMER + 1
    #if (TIMER % 100):
    #    Log()
    time.sleep(.25)
