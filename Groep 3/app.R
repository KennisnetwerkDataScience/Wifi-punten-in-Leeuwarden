#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(leaflet)
library(readr)
library(ggplot2)
library(dplyr)
library(tidyr)
library(leaflet)
library(viridis)
library(lubridate)
library(reshape2)


### Load data 
wifidf.orig <- read_csv2("~/Kennisnetwerk/Wifipunten/locatus/locatusdata_bewerkt.csv", trim_ws = TRUE)

gps_locaties_sensors <- read_csv2("~/Kennisnetwerk/Wifipunten/locatus/gps_locaties_sensors.csv",  trim_ws = TRUE)

### Change some things, join dfs
wifidf <- wifidf.orig %>%
  drop_na(DateTimeLocal) %>%
  rename(ID =VirtualSensorCode) %>%
  left_join(gps_locaties_sensors)  %>%
  mutate(Date = as.Date(DateTimeLocal), 
         Time = format(DateTimeLocal, "%H:%M:%S"), 
         Kwart = format(round_date(DateTimeLocal, "15 minutes"), "%H:%M"))

# Calculate average per 15 minutes. 
wifidf.kwrt <- wifidf %>%
  group_by(ID, lat, lon, Kwart, Date) %>%
  summarise(count = n()) %>%
  summarize(avg = mean(count))


# Make shinyapp
shinyApp(
  ui = fluidPage(
    mainPanel(h3("Hi!"),
              p("De figuur hier onder geeft aan hoeveel adressen er op een bepaald 
                kwartier op verchillende plaatsen zijn. Met de slider kan het gewenste 
                kwartier worden aangegeven. Ook kan er op de startknop worden gedrukt 
                (onderaan het eind van de slider), waardoor een animatie afgespeeld wordt.")),
    sliderInput(inputId = "time", 
                label = "Stel maar in!",
                min = as.POSIXct("00:00", format = "%H:%M"),
                max = as.POSIXct("23:45", format = "%H:%M"),
                value = c(as.POSIXct("00:00", format = "%H:%M")),
                step = 60*15, 
                timeFormat = "%H:%M", 
                animate = animationOptions(interval = 500, loop = TRUE)),
    leafletOutput("MapPlot1")
  ),
  
  server = function(input, output) {
    pal = leaflet::colorFactor(viridis_pal(option = "D")(20), domain = c(0:250))
    output$MapPlot1 <- renderLeaflet({
      leaflet() %>% 
        addProviderTiles(providers$OpenStreetMap) %>% 
        setView(lng = 5.795, lat = 53.2, zoom = 16) %>%
        addLegend("bottomright", pal = pal, values = seq(from = 250, to = 0, by = -50),
                  title = "Gemiddeld aantal bezoekers") 
    })
    
    observe({
    
      tijd <- input$time
      
      
      d = wifidf.kwrt[which(wifidf.kwrt$Kwart == format(tijd, "%H:%M")),]
      
      leafletProxy("MapPlot1")  %>% 
        clearMarkers() %>% 
        addCircleMarkers(data = d,
                         lat = ~lat, 
                         lng = ~lon, 
                         radius = ~sqrt(avg)*1.5,
                         color = ~pal(round(avg,0)),
                         fillColor = ~pal(round(avg,0)), 
                         label = ~as.character(round(avg,0)), 
                         popup = ~as.character(round(avg,0)), 
                         opacity = 0.8,
                         fillOpacity = 0.6,
                         labelOptions = labelOptions(noHide = T))
    })
  }#,
  #options = list(height = 1200)
)

