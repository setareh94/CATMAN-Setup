#!/usr/bin/env python

import Adafruit_LSM9DS0
from decimal import Decimal
from time import sleep
from math import atan2, pi, degrees
#import numpy as np
#import matplotlib.pyplot as plt
# Create new LSM9DS0 instance
imu = Adafruit_LSM9DS0.LSM9DS0()

print("Printing RAW accelerometer, gyroscope and magnetometer values...")
for i in range(10):
    # Get all data
    ACC = imu.rawAccel()
    GYR = imu.rawGyro()
    MAG = imu.rawMag()

    # Convert to strings for display
    strACC = ', '.join(str(num).rjust(5) for num in ACC)
    strGYR = ', '.join(str(num).rjust(5) for num in GYR)
    strMAG = ', '.join(str(num).rjust(5) for num in MAG)

    # Display in a pretty way
    print("Accel: " + strACC + " | Gyro: " + strGYR + " | Mag: " + strMAG)

print("Now Printing Formatted acc. gyro. mag. values: ")
for i in range(10):
	# Multiply the raw values by their appropriate scaling values
	# see page 13 in the LSM9DS0 data-sheet
	AccInGs = [float(num)*0.000732 for num in imu.rawAccel()]
	GyrInDps = [float(num)*0.07 for num in imu.rawGyro()]
	MagInGauss = [float(num)*0.00048 for num in imu.rawMag()]
	# Now we have to format them a little different becasue they have a ton of digits
	dispACC = ', '.join(str("{:.2E}".format(Decimal(num))).rjust(5) for num in AccInGs)
	dispGYR = ', '.join(str("{:.2E}".format(Decimal(num))).rjust(5) for num in GyrInDps)
	dispMag = ', '.join(str("{:.2E}".format(Decimal(num))).rjust(5) for num in MagInGauss)

	print("Accel (g's): " + dispACC + " | Gyro (d/s): " + dispGYR + " | Mag (gauss): " + dispMag)


print("Now we can actually calculate the angles from the Gyro")
gyro_x_angle = 0
for i in range(10):
	DT = 0.05 #50 mili-seconds
	rate_gyr = [float(num)*0.07 for num in imu.rawGyro()]
	gyro_x_angle += rate_gyr[0]*DT
	print(gyro_x_angle)
	sleep(DT)
print("Now we're going to convert the accelerometer values to degrees")

for i in range(10):
	AccXAngle = degrees(atan2(imu.rawAccel()[1],imu.rawAccel()[2])+pi)
	AccYAngle = degrees(atan2(imu.rawAccel()[2],imu.rawAccel()[0])+pi)
	print("X-angle: " + str(AccXAngle) + " Y-angle: " + str(AccYAngle))

print("Now we combine the Data from the Accel. and Gyro. \n" \
	"Using the Complementary Filter: ")

AA = 0.98 # this is some proportion... 
DT = 0.1 # 100ms
CFangleX = 0
CFangleY = 0
for i in range(20):
	rate_gyr = [float(num)*0.07 for num in imu.rawGyro()]
	AccXangle = degrees(atan2(imu.rawAccel()[1],imu.rawAccel()[2])+pi)
	AccYangle = degrees(atan2(imu.rawAccel()[2],imu.rawAccel()[0])+pi)
	# supposidly these lines will convert it such that the accelerometer is
	# zero when the accelerometer is upright...
	AccXangle -= 180.0
	if AccYangle > 90:
		AccYangle -= 270
	else:
		AccYangle += 90

	CFangleX = AA*(CFangleX + rate_gyr[0]*DT) + (1-AA)*AccXAngle
	CFangleY = AA*(CFangleY + rate_gyr[1]*DT) + (1-AA)*AccYAngle
	sleep(DT)

print("Filtered Angle X: {}".format(CFangleX))
print("Filtered Angle Y: {}".format(CFangleY))



#print("Accel: " +  + "g's")

#print('Now attempting to plot some data')

#plt.axis([0, 10, 0, 1])
#plt.ion()

#for i in range(10):
#	y = np.random.random()
#	plt.scatter(i,y)
#	plt.pause(0.05)

