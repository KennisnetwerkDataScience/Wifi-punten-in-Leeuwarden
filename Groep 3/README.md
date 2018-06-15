```
app.R				Code voor het creeren van een shiny app waarin het gemiddeld aantal devices per uur kan worden 
				bekeken (Zie shinyPS.png voor een printscreen van het uiteindelijke resultaat)

connects.py			Onderzoeks programma om te kijken wat de gemiddelde snelheid is van een device tussen de wifi punten.
				Er kwamen negatieve snelheden uit, dus wat extra code op het einde om hier iets meer over te weten te komen.
				Waarschijnlijk loopt de klok op elk wifi meetpunt niet goed, waardoor een devicve eerder kan aankomen dan dat die vertrekt
gps wifi distances.py		Bereken een tabel met de hemelsbrede-afstand in meters tussen de wifi meet punten
kaart.html			Een kaart met de nummers en locatie van de wifi meet punten
kans 30minuten.json		Alle overgangen die binnen 30 minuten aankomen bij het volgende meetpunt, verdeeld naar kans (100%)
leafletPS.png			Printscreen van de interactieve leaflet plot. (test.Rmd
lees in lwd wifi locatus.py	Converteer de geleverde data file naar json formaat met devices die events hebben.
Perdag.Rmd			Code voor het creeren van de interactieve plot, waarin het gemiddeld aantal devices per dag kan worden
				bekeken. (Zie leafletPS.png voor printscreen) 
shinyPS.png			Printscreen van de shiny app (app.R)
```
