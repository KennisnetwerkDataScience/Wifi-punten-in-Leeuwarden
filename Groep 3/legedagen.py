# lege dagen

import json
import datetime

print("Loading")
fp = open("c:/tmp/locatusdata_bewerkt_v2.json","r")
devices = json.load(fp)
fp.close()

dagen = {}
devperdag = {}

print("Counting")
for device in devices:
    for event in devices[device]:
        dt = datetime.datetime.fromtimestamp(event[0])
        dagnr = dt.toordinal()
        if dagnr not in dagen:
            dagen[dagnr] = set()
            devperdag[dagnr] = set()
        dagen[dagnr].add(dt.hour)
        devperdag[dagnr].add(device)

jsonmdagen = {}
for dagnr in range(min(dagen),max(dagen)):
    if dagnr not in dagen:
        print("Op",datetime.datetime.fromordinal(dagnr).date(),"missen alle uren")
        jsonmdagen[str(datetime.datetime.fromordinal(dagnr).date())] = list(range(24))
    else:
        legeuren = set(range(24)) - dagen[dagnr]
        if len(legeuren) > 0:
            print("Op",datetime.datetime.fromordinal(dagnr).date(),"missen de uren",legeuren)
            jsonmdagen[str(datetime.datetime.fromordinal(dagnr).date())] = list(legeuren)
print(json.dumps(jsonmdagen))

# bepaal hoeveel devices er per dag zijn = mate van drukte
devcount = []
for dagnr in range(min(dagen),max(dagen)):
    if dagnr not in devperdag:
        continue
    nrdevs = len(devperdag[dagnr])
    devcount.append(len(devperdag[dagnr]))

devcount.sort()
devcount.reverse()
showtop = 50    # laat de top x drukste dagen zien
i = 0
while showtop > 0:
    for dagnr in devperdag:
        if dagnr not in devperdag:
            continue
        if len(devperdag[dagnr]) == devcount[i]:
            print("Op",datetime.datetime.fromordinal(dagnr).date(),"waren er",devcount[i],"unieke devices")
            showtop -= 1
    i += 1
