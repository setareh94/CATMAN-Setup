from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import argparse
import gps

import Adafruit_LSM9DS0
import time
import csv
# Create new LSM9DS0 instance
imu = Adafruit_LSM9DS0.LSM9DS0()

filename = 'gps1_data.txt'
def uploadToDrive(f):
	global file1
	PARENT_ID = "0B0bl36CBI7q9eTlQcnVHQmxGbzg"

	# Parse the passed arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("files", help="List files to be uploaded.", nargs="+")

	# Define the credentials folder
	home_dir = os.path.expanduser("~")
	credential_dir = os.path.join(home_dir, ".credentials")
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir, "pydrive-credentials.json")

	# Start authentication
	gauth = GoogleAuth()
	# Try to load saved client credentials
	gauth.LoadCredentialsFile(credential_path)
	if gauth.credentials is None:
		# Authenticate if they're not there
		gauth.CommandLineAuth()
	elif gauth.access_token_expired:
		# Refresh them if expired
		gauth.Refresh()
	else:
		# Initialize the saved creds
		gauth.Authorize()
	# Save the current credentials to a file
	gauth.SaveCredentialsFile(credential_path)

	drive = GoogleDrive(gauth)

	# Upload the files
	# for f in parser.parse_args().files:
	#     new_file = drive.CreateFile({"parents": [{"id": PARENT_ID}], "mimeType":"text/plain"})
	#     new_file.SetContentFile(f)
	#     new_file.Upload()

	# file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
	# for file1 in file_list:       
	#     print ("title: %s, id: %s" % (file1['title'], file1['id']))


	# file1 = drive.CreateFile({"parents": [{"id": PARENT_ID}], "mimeType":"text/plain", 'title': 'Hello.txt'})
	file1 = drive.CreateFile({"parents": [{"id": PARENT_ID}], "mimeType":"text/plain"})

	# file1 = drive.CreateFile({'title': 'Hello.txt'})

	file1.SetContentFile(f)
	file1.Upload() # Files.insert()

def deleteShits(file1):
	file1.Delete()

def uploadAccStuff():
	x = 0
	while x<10:
		with open(filename, 'w') as f:

			print('Time, Acc, GYR, Mag')
			# f.write('Time, Acc, GYR, Mag')
			ACC = []
			GYR = []
			MAG = []
			t =[]
			l = 0
			x = 0
			# while x<10:
			while l < 50:
				ACC = imu.rawAccel()
				GYR = imu.rawGyro()
				MAG = imu.rawMag()
				t = time.clock()
				l+=1
				# print(str(t) + '\t' + '{} \t {} \t {}'.format(*ACC) +'\t' + '{} \t {} \t {}'.format(*GYR) \
				#  + '\t' + '{} \t {} \t {}'.format(*MAG))
				f.write(str(t) + '\t' + '{} \t {} \t {}'.format(*ACC) +'\t' + '{} \t {} \t {}'.format(*GYR) \
				 + '\t' + '{} \t {} \t {}'.format(*MAG) + '\n')
		uploadToDrive('acc_data.txt')

		time.sleep(10)
		deleteShits(file1)
		x +=1

def getData():

	session = gps.gps()
	session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
	with open(filename, 'w') as f:

		# uploadAccStuff(f)
		l = 0
		while l < 50:
			try:
				report = session.next()
				# Wait for a 'TPV' report and display the current time
				# To see all report data, uncomment the line below
				print report
				# while l < 100:
				f.write(str(report)+'\n')
				if report['class'] == 'TPV':
					if hasattr(report, 'time'):
						print report.time
						f.write(str(report.time))
					if hasattr(report, 'speed'):
						f.write(" "+str(report.speed * gps.MPS_TO_KPH)+ '\n')
						print report.speed * gps.MPS_TO_KPH
					# 	f.write(str(report.latitude))
					# if hasattr(report, 'altitude'):
					# 	f.write(str(report.altitude))	
					# if hasattr(report, 'longitude'):
					# 	f.write(str(report.longitude))
					l+=1


					# l+=1
			except KeyError:
				pass
			except KeyboardInterrupt:
				quit()
			except StopIteration:
				session = None
				print "GPSD has terminated"
		uploadToDrive('gps1_data.txt')


if __name__ == '__main__':
	# getData()
	uploadAccStuff()
