#!/bin/bash

datadir=data/locatus

grep -vE "^[0-9]+.+DateTimeLocal" $datadir/locatusdata_bewerkt.csv > $datadir/locatusdata_bewerkt_clean.csv
head -n 10001 $datadir/locatusdata_bewerkt_clean.csv > $datadir/locatusdata_bewerkt_clean.10000.csv
