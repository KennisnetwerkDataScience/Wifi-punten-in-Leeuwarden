import json
import datetime

distances = {'1074': {'1074': 0.0, '1078': 101.24931546086312, '1079': 175.5719776445868, '1625': 212.0035304875682, '1627': 101.5810371031637, '1631': 269.24621389071126, '1636': 196.27475043033888, '2054': 132.64082175062813, '2779': 346.70095517260836, '1622': 292.8519185530045}, '1078': {'1074': 101.24931546086312, '1078': 0.0, '1079': 274.77211293755306, '1625': 191.50319681518644, '1627': 80.3756338927891, '1631': 181.97224591113098, '1636': 254.46942757873853, '2054': 227.98849192445317, '2779': 419.4530309975805, '1622': 378.94835996601927}, '1079': {'1074': 175.5719776445868, '1078': 274.77211293755306, '1079': 0.0, '1625': 351.6671963496783, '1627': 267.06983751577513, '1631': 420.5421684313906, '1636': 163.50938444749298, '2054': 114.0806910123181, '2779': 226.84691117970084, '1622': 228.12210262827782}, '1625': {'1074': 212.0035304875682, '1078': 191.50319681518644, '1079': 351.6671963496783, '1625': 0.0, '1627': 119.3448028998378, '1631': 339.459648961501, '1636': 408.2248621419361, '2054': 249.14386034082833, '2779': 554.3088414854551, '1622': 326.8966684338435}, '1627': {'1074': 101.5810371031637, '1078': 80.3756338927891, '1079': 267.06983751577513, '1625': 119.3448028998378, '1627': 0.0, '1631': 255.21273335928765, '1636': 293.95017445785095, '2054': 189.50967412307972, '2779': 448.17960832705444, '1622': 320.93345589344045}, '1631': {'1074': 269.24621389071126, '1078': 181.97224591113098, '1079': 420.5421684313906, '1625': 339.459648961501, '1627': 255.21273335928765, '1631': 0.0, '1636': 331.1161676841916, '2054': 401.8531423723699, '2779': 493.90102714160736, '1622': 558.9318524724505}, '1636': {'1074': 196.27475043033888, '1078': 254.46942757873853, '1079': 163.50938444749298, '1625': 408.2248621419361, '1627': 293.95017445785095, '1631': 331.1161676841916, '1636': 0.0, '2054': 241.31810841924036, '2779': 168.3852394788396, '1622': 387.3031405266773}, '2054': {'1074': 132.64082175062813, '1078': 227.98849192445317, '1079': 114.0806910123181, '1625': 249.14386034082833, '1627': 189.50967412307972, '1631': 401.8531423723699, '1636': 241.31810841924036, '2054': 0.0, '2779': 339.1206979235281, '1622': 164.29407994243977}, '2779': {'1074': 346.70095517260836, '1078': 419.4530309975805, '1079': 226.84691117970084, '1625': 554.3088414854551, '1627': 448.17960832705444, '1631': 493.90102714160736, '1636': 168.3852394788396, '2054': 339.1206979235281, '2779': 0.0, '1622': 438.9512505848288}, '1622': {'1074': 292.8519185530045, '1078': 378.94835996601927, '1079': 228.12210262827782, '1625': 326.8966684338435, '1627': 320.93345589344045, '1631': 558.9318524724505, '1636': 387.3031405266773, '2054': 164.29407994243977, '2779': 438.9512505848288, '1622': 0.0}}

fp = open("c:/tmp/locatusdata_bewerkt_v2.json","r")
locatus = json.load(fp)
fp.close()

wifipoints = []
for wifipoint in distances["1074"]:
    wifipoints.append(wifipoint)
wifipoints.sort()
print(wifipoints)

speeds = {}
for srcpoint in wifipoints:
    speeds[srcpoint] = {}
    for dstnpoint in wifipoints:
        speeds[srcpoint][dstnpoint] = []

tel = 0
for device in locatus:
    lastloc = locatus[device][0][1]
    lasttime = 0
    for event in locatus[device]:
        if event[1] != lastloc and event[0] - lasttime < 1800:
            tel += 1
            speeds[lastloc][event[1]].append(event[0] - lasttime)
        lastloc = event[1]
        lasttime = event[0] + event[2]
print(tel)

kans = {}
avgspeed = {}
for srcpoint in wifipoints:
    kans[srcpoint] = {}
    avgspeed[srcpoint] = {}
    count = 0
    for dstnpoint in wifipoints:
        count += len(speeds[srcpoint][dstnpoint])
    for dstnpoint in wifipoints:
        if dstnpoint == srcpoint:
            avgspeed[srcpoint][dstnpoint] = 0
            kans[srcpoint][dstnpoint] = len(speeds[srcpoint][dstnpoint])*100/count
            continue
        totalsecs = 0
        for i in speeds[srcpoint][dstnpoint]:
            totalsecs += i
        avgspeed[srcpoint][dstnpoint] = distances[srcpoint][dstnpoint]/(totalsecs/count)*60*60
        kans[srcpoint][dstnpoint] = len(speeds[srcpoint][dstnpoint])*100/count
print(kans)
print(avgspeed)


### onderzoeken of er negatieve tijden zijn, en hoevaak die vookomen
tel = 0
for device in locatus:
    lastloc = locatus[device][0][1]
    lasttime = 0
    lastdur = 0
    for event in locatus[device]:
        if event[1] != lastloc:
            if lasttime + lastdur > event[0]:
                if tel < 100:
                    print("device",device)
                    print("left point",lastloc,"at",datetime.datetime.fromtimestamp(lasttime + lastdur),"=",lasttime,"+",lastdur)
                    print("arrived at point",event[1],"at",datetime.datetime.fromtimestamp(event[0]),"(",event[0] - lasttime - lastdur,"seconden)\n")
                tel += 1
        lastloc = event[1]
        lasttime = event[0]
        lastdur = event[2]
print(tel)        
