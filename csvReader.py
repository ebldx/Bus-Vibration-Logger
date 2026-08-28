import requests
import zipfile
import os
import sys
import datetime as dt
import csv
import matplotlib.pyplot as plt
import matplotlib.dates


apiUrl = "https://storage.googleapis.com/storage/v1/b/sarpanit-production/o"


date = {"year" : input("YEAR (yyyy): "), "month" : input("MONTH (mm): "), "day" : input("DAY (dd): ")}

#API PREPARATION
apiResponse = requests.get(apiUrl)
if (apiResponse.ok):
	apiData = apiResponse.json()["items"]
else:
	print(f"Status code: {apiResponse.status_code}")

#SEARCHING FOR FILE TO DOWNLOAD
searchName = f"gtfs/rb_norway-aggregated-gtfs-{date["year"]}{date["month"]}{date["day"]}.zip"
dlLink = None
for file in apiData:
	if (file["name"] == searchName):
		print("File found!")
		dlLink = file["mediaLink"]

#DOWNLOADING
filenameZip = searchName[5:]
try:
	zipFile = open(filenameZip)
	print("Zipfile already present!")
except FileNotFoundError:
	if (dlLink != None):
		print(f"Downloading file from {dlLink}")
		dlReturn = requests.get(dlLink, stream=True)
		totalSize = 0
		with open(filenameZip, mode="wb") as file:
			for chunk in dlReturn.iter_content(chunk_size = 10*1024*1024):
				file.write(chunk)
				totalSize += len(chunk)
				#print(f"{(totalSize/1024)/1024}MB downloaded.")
			file.close()
	else:
		raise Exception("No GTFS file from the provided date was found.")
	print("Download finished!")


#UNZIPPING
dirName = filenameZip[:-5]
try:
	os.mkdir(dirName)
except FileExistsError:
	print("Unzipped file already present!")
unzip_destination = f".\\{dirName}\\"
with zipfile.ZipFile(filenameZip, "r") as gtfsZip:
	gtfsZip.extractall(path=unzip_destination, members=["trips.txt", "stop_times.txt", "stops.txt"])
gtfsZip.close()


#Finding trip ids associated with the route.
routeName = "Sarpsborg-Ise"
routeIds = []
with open(f"{unzip_destination}trips.txt", "r", encoding="utf-8") as tripsFile:
	csvReader = csv.reader(tripsFile, delimiter=",")
	for row in csvReader:
		if (row[3] == routeName):
			routeIds.append(row[1])
tripsFile.close()


#STORING STOP PASSING TIMES FOR ROUTE
stopPassings = []
with open(f"{unzip_destination}stop_times.txt", "r", encoding="utf-8") as stopTimesFile:
	csvReader = csv.reader(stopTimesFile, delimiter=",")
	for row in csvReader:
		if (row[0] in routeIds):
			stopPassings.append(row)
stopTimesFile.close()

#Saving the stop IDs associated with the route.
stopId2Name = {stop[1]:"" for stop in stopPassings}
stopName2Id = {}
with open(f"{unzip_destination}stops.txt", "r", encoding="utf-8") as stopsFile:
	csvReader = csv.reader(stopsFile, delimiter=",")
	for row in csvReader:
		if (row[0] in stopId2Name.keys()):
			stopId2Name[row[0]] = row[1]
			stopName2Id[row[1]] = row[0]
stopsFile.close()

startStopName = None
endStopName = None

print("Valid bus stops:")
for busStop in stopName2Id.keys():
	print(f"\t{busStop}")
print()
while (not(startStopName in stopName2Id.keys())):
	startStopName = input("StartStop: ")
while (not(endStopName in stopName2Id.keys())):
	endStopName = input("Endstop: ")
startStopId = stopName2Id[startStopName]
endStopId = stopName2Id[endStopName]

startDateTime = None
endDateTime = None

csvFileName = input("Vibration csv filename: ")

class BusPassInstance:
	def __init__(self, busRoute:str, startStop:str, endStop:str, dtValues:list, vibValues:list, startDateTime:dt.datetime=None, endDateTime:dt.datetime=None):
		self.busRoute = busRoute
		self.startStop = startStop
		self.endStop = endStop
		self.dtValues = dtValues
		self.vibValues = vibValues
		self.startDateTime = startDateTime
		self.endDateTime = endDateTime
	def plotSelf(self):
		plt.plot(self.dtValues, self.vibValues)
		plt.axis(ymin=0)
		plt.ylabel("Vibration strength")
		plt.xlabel("Datetime")
		if (self.startDateTime and self.endDateTime):
			plt.suptitle(f"Vibration during '{self.busRoute}' bus passing between {self.startDateTime} and {self.endDateTime}")
		else:
			plt.suptitle(f"Vibration during '{self.busRoute}' bus passing between {self.startStop} and {self.endStop}")
		plt.show()

def fetchVibData(csvFileName:str, startDT:dt.datetime, endDT:dt.datetime):
	vibList = []
	dtList = []
	csvFile = csv.reader(open(csvFileName))
	header = next(csvFile)
	for row in csvFile:
			rowDT = dt.datetime(int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5]), int(row[6]))
			if (startDT <= rowDT <= endDT):
				dtList.append(rowDT)
				vibList.append(int(row[-1]))
			elif (rowDT > endDT):
				return dtList, vibList

passInstances = []

for passedStop in stopPassings: #WILL STRUGGLE IF NO STARTSTOP IS DEFINED
	if (passedStop[1] == startStopId):
		hours, minutes, seconds = passedStop[2].split(":")
		startDateTime = dt.datetime(int(date["year"]), int(date["month"]), int(date["day"]), int(hours), int(minutes), int(seconds))
	elif ((passedStop[1] == endStopId) and startDateTime):
		hours, minutes, seconds = passedStop[2].split(":")
		endDateTime = dt.datetime(int(date["year"]), int(date["month"]), int(date["day"]), int(hours), int(minutes), int(seconds))
		x, y = fetchVibData(csvFileName, startDateTime, endDateTime)
		passInstances.append(BusPassInstance(routeName, startStopName, endStopName, x, y))
		startDateTime = None
		endDateTime = None

for busPass in passInstances:
	busPass.plotSelf()