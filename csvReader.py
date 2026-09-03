import requests
import zipfile
import os
import pathlib as pl
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
if (os.path.exists(filenameZip)):
	print("Zipfile already present!")
else:
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
if (os.path.exists(dirName)):
	print("Unzipped file already present!")
else:
	os.mkdir(dirName)
unzip_destination = pl.Path(dirName)
with zipfile.ZipFile(filenameZip, "r") as gtfsZip:
	gtfsZip.extractall(path=unzip_destination, members=["trips.txt", "stop_times.txt", "stops.txt"])


#Finding route name.
routeName = None
routeNameList = []
with open(unzip_destination / "trips.txt", "r", encoding="utf-8") as tripsFile:
	csvReader = csv.DictReader(tripsFile, delimiter=",")
	for row in csvReader:
		if (not(row["trip_headsign"] in routeNameList)):
			routeNameList.append(row["trip_headsign"])

while (not(routeName in routeNameList)):
	search = input("\nSearch for a route: ").strip().lower()
	matches = [route for route in routeNameList if search in route.lower()]
	print("Results:")
	for name in matches:
		print(f"\t{name}")
	routeName = input("Insert a valid route name: ")

#Finding trip ids associated with the route.
print("Finding trip IDs associated with the route...")
routeIds = []
with open(unzip_destination / "trips.txt", "r", encoding="utf-8") as tripsFile:
	csvReader = csv.DictReader(tripsFile, delimiter=",")
	for row in csvReader:
		if (row["trip_headsign"] == routeName):
			routeIds.append(row["trip_id"])


#STORING STOP PASSING TIMES FOR ROUTE
print("Saving valid stop passing timestamps...")
stopPassings = []
with open(unzip_destination / "stop_times.txt", "r", encoding="utf-8") as stopTimesFile:
	csvReader = csv.DictReader(stopTimesFile, delimiter=",")
	for row in csvReader:
		if (row["trip_id"] in routeIds):
			stopPassings.append(row)

#Saving the stop IDs associated with the route.
print("Saving valid stop IDs...")
stopId2Name = {stop["stop_id"]:"" for stop in stopPassings}
stopName2Id = {}
with open(unzip_destination / "stops.txt", "r", encoding="utf-8") as stopsFile:
	csvReader = csv.DictReader(stopsFile, delimiter=",")
	for row in csvReader:
		if (row["stop_id"] in stopId2Name.keys()):
			stopId2Name[row["stop_id"]] = row["stop_name"]
			stopName2Id[row["stop_name"]] = row["stop_id"]

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
	with open(csvFileName) as csvFile:
		csvReader = csv.DictReader(csvFile)
		for row in csvReader:
				rowDT = dt.datetime(int(row["year"]), int(row["month"]), int(row["day"]), int(row["hour"]), int(row["minute"]), int(row["second"]))
				if (startDT <= rowDT <= endDT):
					dtList.append(rowDT)
					vibList.append(int(row["vibration"]))
				elif (rowDT > endDT):
					return dtList, vibList
	return dtList, vibList

tripId = None
passInstances = []
print("Saving stop passings...")
for passedStop in stopPassings:
	if (passedStop["stop_id"] == startStopId):
		hours, minutes, seconds = passedStop["arrival_time"].split(":")
		startDateTime = dt.datetime(int(date["year"]), int(date["month"]), int(date["day"]), int(hours), int(minutes), int(seconds))
		tripId = passedStop["trip_id"]
	elif ((passedStop["stop_id"] == endStopId) and startDateTime and (tripId == passedStop["trip_id"])):
		hours, minutes, seconds = passedStop["departure_time"].split(":")
		endDateTime = dt.datetime(int(date["year"]), int(date["month"]), int(date["day"]), int(hours), int(minutes), int(seconds))
		x, y = fetchVibData(csvFileName, startDateTime, endDateTime)
		passInstances.append(BusPassInstance(routeName, startStopName, endStopName, x, y))
		startDateTime = None
		endDateTime = None
		tripId = None

for busPass in passInstances:
	vibDetected = False
	for vibration in busPass.vibValues:
		if (vibration > 0):
			vibDetected = True
	if (vibDetected):
		busPass.plotSelf()