# packages
library(leaflet)
library(dplyr)

loc <- read.csv('~/OpenData/leeuwarden_data/locatus/locatusdata_bewerkt.csv', sep = ';') %>% 
  as_tibble() %>%
  mutate(DateTimeLocal = ymd_hms(DateTimeLocal),
         uur = hour(DateTimeLocal),
         dagdeel = ifelse(uur < 6, 'nacht',
                         ifelse(uur < 12, 'ochtend',
                                ifelse(uur < 18, 'middag', 'avond'))),
         dagdeel = factor(dagdeel, c('ochtend', 'middag', 'avond', 'nacht'), ordered = T),
         weekdag = wday(DateTimeLocal, label = T, abbr = F)) %>%
  filter(!is.na(DateTimeLocal))

# opslaan
save(loc, file = '~/OpenData/leeuwarden_data/locatus/locatus.Rda')

# data locatus (Rda)
load('~/OpenData/leeuwarden_data/locatus/locatus.Rda') 

# per minuut per meetpunt
per_minuut <- loc %>%
  mutate(minuut = floor_date(DateTimeLocal, 'minute')) %>%
  count(VirtualSensorCode, minuut) 

save(per_minuut, file = '~/OpenData/leeuwarden_data/locatus/per_minuut.Rda')

# locatie sensoren
sensoren <- read.csv('~/OpenData/leeuwarden_data/locatus/gps_locaties_sensors.csv', sep = ';') %>%
  as_tibble() %>%
  mutate_at(vars(contains('ude')), function(x) gsub(',', '.', x)) %>%
  mutate_at(vars(contains('ude')), as.numeric) %>%
  rename(lon = latitude,
         lat = longitude)

# parkeergegevens 

# garages
parkeergarages_capaciteit <- read.csv('~/OpenData/leeuwarden_data/parkeerdata/leeuwarden_garage_parking_garage.csv', sep =';')
parkeergarages <- read.csv('~/OpenData/leeuwarden_data/parkeerdata/leeuwarden_garage_parking_garage_gps.csv', 
                           sep = ';') %>%
  as_tibble() %>%
  mutate_at(vars(contains('ude')), function(x) gsub(',', '.', x)) %>%
  mutate_at(vars(contains('ude')), as.numeric) %>%
  left_join(parkeergarages_capaciteit)

# transacties: garage
trans_garage <- read.csv('~/OpenData/leeuwarden_data/parkeerdata/leeuwarden_garage_parking_transactions.csv', 
                                      sep = ';') %>% 
  as_tibble() %>%
  mutate_at(vars(contains('dt')), dmy_hm) %>%
  mutate(card_type_id = ifelse(card_type_id == 220, 'kort', 
                               ifelse(card_type_id == 221, 'abo', NA)))

# transacties: mobile
trans_mobile <- read.csv('~/OpenData/leeuwarden_data/parkeerdata/leeuwarden_mobile_parking_transactions.csv', 
                         sep = ';') %>%
  as_tibble() %>%
  mutate_at(vars(contains('dt')), dmy_hm)

# transacties: street
trans_street <- read.csv('~/OpenData/leeuwarden_data/parkeerdata/leeuwarden_street_parking_transactions.csv', 
                         sep = ';') %>%
  as_tibble() %>%
  mutate_at(vars(contains('dt')), dmy_hm)
trans_street

# tarieven
tarief <- read_excel('~/OpenData/leeuwarden_data/parkeerdata/parkeerautomaten_zones_en_tarieven_2017.xlsx')

# knmi
knmi <- read.csv('~/OpenData/leeuwarden_data/knmi/knmi_uurgeg_270_2011-2020_leeuwarden.csv', sep = ';') %>% 
  as_tibble() %>%
  select(datum = YYYYMMDD,
         uurvak = HH,
         wind = FH,
         temperatuur = T,
         zonduur = SQ,
         globstraling = Q,
         neerslagduur = DR,
         neerslag = RH,
         zicht = VV,
         bewolking = N,
         mist = M,
         regen = R,
         sneeuw = S,
         onweer = O,
         ijs = Y) %>%
  mutate(zonduur = ifelse(zonduur == -1, 0, zonduur),
         neerslag = ifelse(neerslag == -1, 0, neerslag),
         temperatuur = temperatuur/10,
         uurvak = as.character(uurvak),
         uurvak = ifelse(nchar(uurvak) == 1,  paste0('0',uurvak), uurvak),
         tijd = paste0(datum,uurvak),
         tijd = ymd_h(tijd)) %>%
  select(-datum, -uurvak) %>%
  filter(tijd > min(loc$DateTimeLocal))

save(knmi, file = '~/OpenData/leeuwarden_data/knmi/knmi.Rda')

knmi %>%
  ggplot(aes(tijd, neerslag)) +
  geom_line()
