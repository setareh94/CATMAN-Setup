#!/usr/bin/python

#
#Test code for GPIO switching
#will be used to control 
#antenna switching
#

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13,GPIO.OUT) 
GPIO.setup(19,GPIO.OUT)
GPIO.output(13,GPIO.HIGH)
time.sleep(4)
GPIO.output(13,GPIO.LOW)
time.sleep(2)
GPIO.output(19,GPIO.HIGH)
time.sleep(2)
GPIO.output(19,GPIO.LOW)
