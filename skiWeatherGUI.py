from tkinter import Tk, Label, ttk, StringVar, Button, IntVar
from datetime import datetime, timedelta
from weatherScraper import WeatherScraper
from skiLubrication import SkiLubrication
from snowDepthScraper import SnowDepthScraper

class SkiWeatherGUI:
    # class for creating a ski weather summary GUI
    def __init__(self, master):
        
        self._master = master
        self._master.title("Ski weather checker")
        self._master.geometry("600x350")
        
        #fonts
        boldFont = ("Helvetica", 10, "bold")
        regularFont = ("Helvetica", 10)

        self._temperatures = []
        
        # defining urls to be used by scrapers
        self._firstPartUrlWeather = "https://www.yr.no/nb/v%C3%A6rvarsel/timetabell/"
        self._firstPartUrlSnowDepth = "https://www.skiforeningen.no/utimarka/foremelding/"
        self._placesUrls = {"Linderudkollen": {"weather": "2-11844463/Norge/Oslo/Oslo/Linderudkollen", "snowDepth": 'lillomarka-og-gjellerasen/#:~:text=Linderudkollen%20-%2006.&text=Vær%3A,20-50%20cm.'},
                            "Rustadsaga": {"weather": "2-11817724/Norge/Oslo/Oslo/Rustadsaga", "snowDepth": 'ostmarka'},
                            "Finnemarka": {"weather": "1-72002/Norge/Viken/Modum/Finnemarka", "snowDepth": 'finnemarka/'},
                            "Sollihøgda": {"weather": "1-72655/Norge/Viken/Bærum/Sollihøgda", "snowDepth": "krokskogen/"},
                            "Losby": {"weather": "1-74008/Norge/Viken/Lørenskog/Losby", "snowDepth": 'ostmarka'}}
        
        # input widgets
        whereLabel = Label(master, text="Where do you want to ski?", font=regularFont)
        whereLabel.grid(row=0, column=0, sticky="w", columnspan=2, pady=1, ipadx=3)
        
        self._places = StringVar()
        self._placesChosen = ttk.Combobox(master, width=15, textvariable=self._places)
        self._placesChosen["values"] = list(self._placesUrls.keys())
        self._placesChosen.grid(row=1, column=0, pady=5, sticky="w", columnspan=2, padx=3)
        self._placesChosen.current(0)

        timeLabel = Label(master, text="When do you want to ski?", font=regularFont)
        timeLabel.grid(row=2, column=0, sticky="w", columnspan=2, pady=1, ipadx=3)

        dateLabel = Label(master, text="Date", font=regularFont)
        dateLabel.grid(row=3, column=0)

        fromHourLabel = Label(master, text="From (hour)", font=regularFont)
        fromHourLabel.grid(row=3, column=1)

        durationLabel = Label(master, text="Duration (hours)", font=regularFont)
        durationLabel.grid(row=3, column=2)

        self._day = StringVar()
        self._dayChosen = ttk.Combobox(master, width=10, textvariable= self._day)
        self._dayChosen["values"] = self._getDates()
        self._dayChosen.grid(row=4, column=0, padx=3, pady=5, sticky="w")
        self._dayChosen.current(0)

        self._hour = StringVar()
        self._hourChosen = ttk.Combobox(master, width=10, textvariable= self._hour)
        self._hourChosen.grid(row=4, column=1, padx=10, sticky="w")
        self._getHours()

        self._dayChosen.bind("<<ComboboxSelected>>", self._setHours)

        self._duration = IntVar()
        self._durationChosen = ttk.Combobox(master, width=10, textvariable=self._duration)
        self._durationChosen['values'] = [x for x in range(1, 31)]
        self._durationChosen.grid(row=4, column=2)
        self._durationChosen.current(3)

        execute = Button(master, bg="cyan", text="Check", command=self._addWeatherAndLubricationInfo)
        execute.grid(row=5, column=1)
        
        # output widgets
        self._descTitleLabel = Label(master, text="Weather", font=boldFont)
        self._descTitleLabel.grid(row=6, column=0, sticky="w", ipadx=3, pady=2)

        self._descLabel = Label(master, font=regularFont)
        self._descLabel.grid(row=6, column=1, columnspan=8, sticky="w")
        
        self._temperatureTitleLabel = Label(master, text = "Temperature", font=boldFont)
        self._temperatureTitleLabel.grid(row=7, column=0, sticky="w", ipadx=3, pady=2)

        self._temperatureLabel = Label(master, font=regularFont)
        self._temperatureLabel.grid(row=7, column=1, columnspan=8, sticky="w")
        
        self._windTitleLabel = Label(master, text="Winds", font=boldFont)
        self._windTitleLabel.grid(row=8, column=0, sticky="w", ipadx=3, pady=2)
        
        self._windLabel = Label(master, font=regularFont)
        self._windLabel.grid(row=8, column=1, columnspan=8, sticky="w")

        self._precipitationTitleLabel = Label(master, text="Precipitation", font=boldFont)
        self._precipitationTitleLabel.grid(row=9, column=0, rowspan=3, sticky="nw", ipadx=3, pady=2)

        self._precipitationLabel = Label(master, justify="left", font=regularFont)
        self._precipitationLabel.grid(row=9, column=1, columnspan=8, sticky="w")
        
        self._lubricationTitleLabel = Label(master, text="Lubrication", font=boldFont)
        self._lubricationTitleLabel.grid(row=10, column=0, sticky="w", ipadx=3, pady=2)

        self._lubricationLabel = Label(master, font=regularFont)
        self._lubricationLabel.grid(row=10, column=1, columnspan=9, sticky="w")
        
        self._snowDepthTitleLabel = Label(master, text="Snow depth", font=boldFont)
        self._snowDepthTitleLabel.grid(row=11, column=0, sticky="w", ipadx=3, pady=2)
        
        self._snowDepthLabel = Label(master, font=regularFont)
        self._snowDepthLabel.grid(row=11, column=1, columnspan=8, sticky="w")
        
    # adds info about weather, ski lubrication and snow depth
    def _addWeatherAndLubricationInfo(self):
        self._addWeatherInfo()
        self._addLubricationInfo()
        self._setSnowDepthLabel()
    
    # sets snow depth label
    def _setSnowDepthLabel(self):
        place = self._places.get()
        url = self._firstPartUrlSnowDepth + self._placesUrls[place]["snowDepth"]
        snowDepthRetriever = SnowDepthScraper(url, place)
        snowDepthInfo = snowDepthRetriever.getInfo()
        if len(snowDepthInfo) != 0:
            snowDepth = snowDepthInfo[0]
            monthDict = {"januar": "01", "februar": "02", "mars": "03", "april": "04", "mai": "05", "juni": "06",
            "juli": "07", "august": "08", "september": "09", "oktober": "10", "november": "11", "desember": "12"}
            
            day = snowDepthInfo[1][0]; month = monthDict[snowDepthInfo[1][1].lower()]
            year = snowDepthInfo[1][2][2:]
            
            alternatePlace = snowDepthInfo[2]
            # if info is taken from somewhere else, the alternate place is provided
            if alternatePlace != "":
                alternatePlace = " " + alternatePlace
            
            text = f"{snowDepth} (Updated {day}.{month}.{year}{alternatePlace})"
        else:
            text = f"No snow depth info found for {place}"
        
        self._snowDepthLabel.config(text=text)
            
    # adds different weather metrics
    def _addWeatherInfo(self):
        day = self._dayChosen.current()
        fromHour = int(self._hour.get())
        duration = self._duration.get()
        url = self._firstPartUrlWeather + self._placesUrls[self._places.get()]["weather"]
        weatherInfo = WeatherScraper(url, day, fromHour, duration)
        self._setWeatherDescription(weatherInfo.getWeatherDescriptions())
        self._temperatures = weatherInfo.getTemperatures()
        self._setTemperatureLabel(self._temperatures)
        self._setWindLabel(weatherInfo.getWinds(), weatherInfo.getWindGusts())
        self._setPrecipitationLabel(weatherInfo.getMinAndMaxPrecipitation())
    
    # adds tip about ski lubrication
    def _addLubricationInfo(self):
        lubricator = SkiLubrication(self._temperatures)
        lubricants = lubricator.getLubricationTip()

        if len(lubricants) == 0:
            text = f"No good lube suggestions in these temperatures"
        elif len(lubricants) == 1:
            text = f"For grip you should use {lubricants[0]} lube"
        elif len(lubricants) == 2:
            text = f"For grip you should mainly use {lubricants[0]} lube, but also bring {lubricants[1]} lube"
        elif len(lubricants) > 2:
            text = f"For grip you should mainly use {lubricants[0]} lube, but also bring {lubricants[1]}"
            for i in range(2, len(lubricants)):
                if i == len(lubricants) - 1:
                    text += f" and {lubricants[i]} lube"
                else:
                    text += f",{lubricants[i]} "

        self._lubricationLabel.config(text=text)
    
    # sets precipitation label
    def _setPrecipitationLabel(self, minAndMaxPrecipitations):
        types = ["Snow", "Sleet", "Rain"]
        text = ""
        # looping through how much precipitation for snow, sleet and rain. Only provide info if present
        for index, precipType in enumerate(minAndMaxPrecipitations):
            if precipType[1] != 0:
                if text != "":
                    text += "\n"       
                if round(precipType[0], 1) == 0.0:
                    text += f"{types[index]}: Expect up to {precipType[1]:.1f}mm"
                else:
                    text += f"{types[index]}: Expect precipitation between {precipType[0]:.1f}mm and {precipType[1]:.1f}mm"
        if text == "":
            text = f"{types[index]}: No precipitation expected"

        self._precipitationLabel.config(text=text)
        
    # sets wind label
    def _setWindLabel(self, winds, gusts):
        maxWind = max(winds)
        
        text = f"Max wind will be {maxWind} m/s"
        # gust info could be missing from yr.no
        if len(gusts) > 0:
            maxGust = max(gusts)
            text += f" with gusts up to {maxGust} m/s"

        self._windLabel.config(text=text)
    
    # sets temperature label
    def _setTemperatureLabel(self, temperatures):
        minTemp = min(temperatures)
        maxTemp = max(temperatures)

        numOfUniqueValues = len(set(temperatures))
        
        # provide temperature range if difference between min and max
        if numOfUniqueValues == 1:
            text = f"The temperature will stay at {maxTemp}°C"
        else:
            text = f"The temperature will range from {minTemp}°C to {maxTemp}°C "

        self._temperatureLabel.config(text=text)
    
    # sets weather description label
    def _setWeatherDescription(self, weatherDescriptions):
        weatherDictionary = {'tåke': 'foggy', 'skyet': 'cloudy', 'delvis skyet': 'partly cloudy',
                             'lettskyet': 'some clouds', 
                             'lett regn': 'light rain', 'regn': 'rain', 'kraftig regn': 'heavy rain',
                             'klarvær': 'clear skies',
                             'lett snø': 'light snow', 'snø': 'snow', 'kraftig snø': 'heavy snow',
                             'lett sludd': 'light sleet', 'sludd': 'sleet', 'kraftig sludd': 'heavy sleet'}

        uniqueDescriptions = []
        for description in weatherDescriptions:
            if description not in uniqueDescriptions:
                uniqueDescriptions.append(description)
        
        # provide all possible descriptions of weather
        if len(uniqueDescriptions) == 1:
            text = f"You can expect it to be {weatherDictionary[uniqueDescriptions[0]]} in the timeframe"
        else:
            text = f"The weather will go from {weatherDictionary[uniqueDescriptions[0]]}"
            for i in range(1, len(uniqueDescriptions)):
                text += f" to {weatherDictionary[uniqueDescriptions[i]]}"
        self._descLabel.config(text=text)
    
    # get dates for combobox
    def _getDates(self):
        today = datetime.now().strftime("%a %d.%m")
        dates = [today]

        for i in range(1, 3):
            nextDate = (datetime.now() + timedelta(i)).strftime("%a %d.%m")
            dates.append(nextDate)

        return dates
    
    # set hours for combobox
    def _setHours(self, event):
        hours = []
        # if today is chosen only the remaining hours of the day will be shown
        if self._day.get() == self._getDates()[0]:  # today
            thisHour = (datetime.now() + timedelta(hours=1)).strftime("%H")
            hours.append(thisHour)
            for i in range(1, 24 - (int(thisHour))):
                nextHour = (datetime.now() + timedelta(hours=i+1)).strftime("%H")
                hours.append(nextHour)
        else:
            for i in range(24):
                hour = (datetime.now() + timedelta(hours=i)).strftime("%H")
                hours.append(hour)
            hours.sort()

        self._hourChosen["values"] = hours
        if self._day.get() == self._getDates()[0]:
            self._hourChosen.current(0)
        else:
            # show time 09 as default if day is not today
            self._hourChosen.current(9)

    # get hours for combobox when starting up program
    def _getHours(self):
        hours = []
        if self._day.get() == self._getDates()[0]: # today
            thisHour = (datetime.now() + timedelta(hours=1)).strftime("%H")
            hours.append(thisHour)
            for i in range(1, 24-(int(thisHour))):
                nextHour = (datetime.now() + timedelta(hours=i+1)).strftime("%H")
                hours.append(nextHour)

        self._hourChosen["values"] = hours
        
        self._hourChosen.current(0)


master = Tk()
myGUI = SkiWeatherGUI(master)
master.mainloop()