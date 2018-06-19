import json

print("Loading")
fp = open("c:/tmp/locatusdata_bewerkt_v2.json","r")
devices = json.load(fp)
fp.close()

timepruning = 30 * 60     # stop eventreeks als de tijd tussen twee wifi punten groter is als..
telroutes = {}
reekscount = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]
def zoekroutes(eventreeks):
    # weet nog niet
    if len(eventreeks) not in telroutes:
        telroutes[len(eventreeks)] = 1
    else:
        telroutes[len(eventreeks)] += 1
    if len(eventreeks) <= 1:
        return     # reeks is te kort, skip
    for routelen in range(2,11):
        for i in range(0,len(eventreeks) - routelen):
            reeks = eventreeks[i:i+routelen]
            p = reekscount[routelen]
            for punt in reeks:
                if punt not in p:
                    p[punt] = {}
                p = p[punt]
            if "count" in p:
                p["count"] += 1
            else:
                p["count"] = 1
    return

print("Finding routes")
for device in devices:
    eventreeks = []
    lastwifi = "9999"    # daar ben je nooit, dus eerste punt toevoegen
    lasttime = devices[device][0][0]    # wanneer als laatste gezien
    for event in devices[device]:
        if lastwifi == event[1]:    # dus hetzelfde wifi punt
            lasttime = event[0]
            continue
        if event[0] - lasttime < timepruning:
            # dit event was binnen de tijd, dus voeg toe
            eventreeks.append(event[1])
        else:
            # reeks gevonden, dus verwerken...
            
            zoekroutes(eventreeks)
            eventreeks = []
        lastwifi = event[1]
        lasttime = event[0]
    if len(eventreeks) > 0:     # zijn er nog onverwerkte event reeksen ?
        zoekroutes(eventreeks)

def gettop10routes(tree,depth):
    #print("depth=",depth)
    ret = []
    if depth == 0:
        if len(tree) != 1:
            errorsfgdsfg
        return [(tree["count"],None)]
    for i in tree:
        #print("i=",i)
        x = gettop10routes(tree[i],depth-1)
        #print("x=",x)
        for j in x:
            #print("j=",j)
            if j[1]:
                ret.append((j[0],i + "-" + j[1]))
            else:
                ret.append((j[0],i ))
    ret.sort()
    if len(ret) > 10:
        ret = ret[len(ret)-10:]
    #print("ret=",ret)
    return ret

#print(gettop10routes(reekscount[3],3))
#sfgsgds
for rlength in range(2,11):
    print("Top 10 route met lengte",rlength)
    ret = gettop10routes(reekscount[rlength],rlength)
    ret.reverse()
    for i in ret:
        print("{}x de route {}".format(i[0],i[1]))
    print("")
    
