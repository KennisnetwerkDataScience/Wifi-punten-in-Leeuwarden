# inlezen wifi lwd

import csv
import datetime
import json

devices = {}
lines = 0
with open("C:/Users/Tjibbe/Downloads/lwd wifi/leeuwarden_data/locatus/locatusdata_bewerkt.csv") as csvfile:
    csvreader = csv.DictReader(csvfile,delimiter=";")
    for row in csvreader:
        #id	VirtualSensorCode	DateTimeLocal	Duration	code_address
        if row["DateTimeLocal"] == "DateTimeLocal":      # if header is there again,skip
            continue
        VirtualSensorCode = row["VirtualSensorCode"]
        DateTimeLocal = int(datetime.datetime.strptime(row["DateTimeLocal"], "%Y-%m-%d %H:%M:%S").timestamp())
        Duration = row["Duration"]
        if Duration == "":    # if no duration specified, set it to 0
            Duration = 0
        else:
            Duration = int(float(Duration))
        code_address = row["code_address"]
        lines += 1

        if code_address in devices:
            devices[code_address].append((DateTimeLocal,VirtualSensorCode,Duration))
        else:
            devices[code_address] = [(DateTimeLocal,VirtualSensorCode,Duration)]

print("Aantal regels informatie",lines)
print("Aantal unieke devices",len(devices))
for device in devices:
    devices[device].sort()       # sort on timestamp
    
fp = open("locatusdata_bewerkt_v2.json","w")
json.dump(devices,fp)
fp.close()
# voorbeeld van json uitvoer: device 1537467 heeft de volgende "events", dus (wifi-punt,unix-timestamp,duur)
#{"1537467": [["1622", 1500160345.0, "0.0"], ["2779", 1494504330.0, "0.0"], ["2779", 1494337096.0, "0"], ["1074", 1491704952.0, "0.0"], ["1074", 1497033817.0,
