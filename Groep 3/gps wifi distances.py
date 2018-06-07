#https://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
from math import radians, cos, sin, asin, sqrt
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    mdistance = 6371000* c
    return mdistance

#sensor_id       latitude	longitude   naam
gps_locaties_sensors = """1074;53,200509;5,794506;Coolcat / Nieuwestad
1078;53,200826;5,793081;We / Nieuwestad
1079;53,200347;5,797128;We / Wirdumerdijk
1625;53,199183;5,792219;Albert Heijn/ Prins Hendrikstraat
1627;53,200104;5,793139;No Nonsens/Ruiterskwartier
1631;53,202216;5,791639;Eric Steenbergen Designwinkel / Kleine Kerkstraat
1636;53,201777;5,796556;Zenzi / Sint Jacobsstraat
2054;53,199645;5,795879;Winkelcentrum Zaailand / Ruiterskwartier
2779;53,202032;5,799048;Cafe Blikspuit / Over de Kelders
1622;53,198300;5,796900;Wirdumerpoortsbrug brugwachtershuisje""".split("\n")

sensors = {}
for row in gps_locaties_sensors:
    sensor = row.split(";")
    sensors[sensor[0]] = (float(sensor[1].replace(",",".")),float(sensor[2].replace(",",".")))
#print(sensors)

distance = {}
for frompoint in sensors:
    distance[frompoint] = {}
    for topoint in sensors:
        distance[frompoint][topoint] = haversine(sensors[frompoint][1],sensors[frompoint][0],sensors[topoint][1],sensors[topoint][0])
print(distance)
