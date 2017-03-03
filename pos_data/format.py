#!/usr/bin/env python

import CATMAN_LSM9DS0
import time
import csv
# Create new LSM9DS0 instance
imu = CATMAN_LSM9DS0.LSM9DS0()


#print("Printing RAW accelerometer, gyroscope and magnetometer values...")
print('Time, Acc, GYR, Mag')

ACC = []
GYR = []
MAG = []
t =[]
l = 0
while l < 1000:
	ACC = imu.rawAccel()
	GYR = imu.rawGyro()
	MAG = imu.rawMag()
	t = time.clock()
	l+=1
	#print(str(t) + '\t' + '{} \t {} \t {}'.format(*ACC) +'\t' + '{} \t {} \t {}'.format(*GYR) \
	 #+ '\t' + '{} \t {} \t {}'.format(*MAG))

	
