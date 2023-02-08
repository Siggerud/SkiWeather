from tkinter import Tk, Label, ttk, StringVar, Button
from datetime import datetime, timedelta
from scraper import WeatherScraper
from skiLubrication import SkiLubrication

class SkiWeatherGUI:
    def __init__(self, master):
        self._master = master
        self._master.title("Ski weather checker")
        self._master.geometry("400x400")

        self._temperatures = []

        whereLabel = Label(master, text="Where do you want to ski?")
        whereLabel.grid(row=0, column=0, sticky="w", columnspan=2, pady=1)

        self._firstPartUrl = "https://www.yr.no/nb/v%C3%A6rvarsel/timetabell/"
        self._placesUrls = {"Badedammen": "1-2226455/Norge/Oslo/Oslo/Badedammen",
                            "Nøklevann": "1-74028/Norge/Oslo/Oslo/N%C3%B8klevannet",
                            "Finnemarka": "1-72002/Norge/Viken/Modum/Finnemarka",
                            "Sollihøgda": "1-72655/Norge/Viken/Bærum/Sollihøgda"}

        self._places = StringVar()
        self._placesChosen = ttk.Combobox(master, width=15, textvariable=self._places)
        self._placesChosen["values"] = list(self._placesUrls.keys())
        self._placesChosen.grid(row=1, column=0, pady=5, sticky="w", columnspan=2)
        self._placesChosen.current(0)

        timeLabel = Label(master, text="When do you want to ski?")
        timeLabel.grid(row=2, column=0, sticky="w", columnspan=2, pady=1)

        dateLabel = Label(master, text="Date")
        dateLabel.grid(row=3, column=0)

        fromHourLabel = Label(master, text="From")
        fromHourLabel.grid(row=3, column=1)

        toHourLabel = Label(master, text="To")
        toHourLabel.grid(row=3, column=2)

        self._day = StringVar()
        self._dayChosen = ttk.Combobox(master, width=10, textvariable= self._day)
        self._dayChosen["values"] = self._getDates()
        self._dayChosen.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self._dayChosen.current(0)

        self._hour = StringVar()
        self._hourChosen = ttk.Combobox(master, width=10, textvariable= self._hour)
        self._hourChosen.grid(row=4, column=1, padx=10, sticky="w")

        self._dayChosen.bind("<<ComboboxSelected>>", self._setHours)

        self._toHour = StringVar()
        self._toHourChosen = ttk.Combobox(master, width=10, textvariable=self._toHour)
        self._getHours()
        self._toHourChosen.grid(row=4, column=2)
        self._hourChosen.current(0)
        self._toHourChosen.current(0)

        self._hourChosen.bind("<<ComboboxSelected>>", self._setToHours)

        execute = Button(master, bg="cyan", text="Check", command=self._addWeatherAndLubricationInfo)
        execute.grid(row=5, column=1)

        self._descLabel = Label(master)
        self._descLabel.grid(row=6, column=0, columnspan=4, sticky="w")

        self._temperatureLabel = Label(master)
        self._temperatureLabel.grid(row=7, column=0, columnspan=4, sticky="w")

        self._windLabel = Label(master)
        self._windLabel.grid(row=8, column=0, columnspan=4, sticky="w")

        self._precipitationLabel = Label(master)
        self._precipitationLabel.grid(row=9, column=0, columnspan=4, sticky="w")

        self._lubricationLabel = Label(master)
        self._lubricationLabel.grid(row=10, column=0, columnspan=4, sticky="w")

    def _addWeatherAndLubricationInfo(self):
        self._addWeatherInfo()
        self._addLubricationInfo()
    def _addWeatherInfo(self):
        day = self._dayChosen.current()
        fromHour = int(self._hour.get())
        toHour = int(self._toHour.get())
        url = self._firstPartUrl + self._placesUrls[self._places.get()]
        weatherInfo = WeatherScraper(url, day, fromHour, toHour)
        self._setWeatherDescription(weatherInfo.getWeatherDescriptions())
        self._temperatures = weatherInfo.getTemperatures()
        self._setTemperatureLabel(self._temperatures)
        self._setWindLabel(weatherInfo.getWinds(), weatherInfo.getWindGusts())
        self._setPrecipitationLabel(weatherInfo.getMinAndMaxPrecipitation())

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
                    text += f"and {lubricants[i]} lube"
                else:
                    text += f",{lubricants[i]} "

        self._lubricationLabel.config(text=text)

    def _setPrecipitationLabel(self, minAndMaxPrecipitation):
        if minAndMaxPrecipitation[1] != 0:
            text = f"Expect precipitation between {minAndMaxPrecipitation[0]}mm and {minAndMaxPrecipitation[1]}mm"
        else:
            text = "No precipitation expected"

        self._precipitationLabel.config(text=text)
    def _setWindLabel(self, winds, gusts):
        maxWind = max(winds)
        maxGust = max(gusts)

        text = f"Max wind will be {maxWind} m/s with gusts up to {maxGust} m/s"

        self._windLabel.config(text=text)

    def _setTemperatureLabel(self, temperatures):
        minTemp = min(temperatures)
        maxTemp = max(temperatures)

        numOfUniqueValues = len(set(temperatures))

        if numOfUniqueValues == 1:
            text = f"The temperature will stay at {maxTemp}°C"
        else:
            text = f"The temperature will range from {minTemp}°C to {maxTemp}°C "

        self._temperatureLabel.config(text=text)

    def _setWeatherDescription(self, weatherDescriptions):
        weatherDictionary = {'tåke': 'foggy', 'skyet': 'cloudy', 'delvis skyet': 'partly cloudy',
                             'lettskyet': 'some clouds', 'regn': 'rain', 'klarvær': 'no clouds'}

        uniqueDescriptions = []
        for description in weatherDescriptions:
            if description not in uniqueDescriptions:
                uniqueDescriptions.append(description)

        if len(uniqueDescriptions) == 1:
            text = f"You can expect it to be {weatherDictionary[uniqueDescriptions[0]]} in the timeframe"
        else:
            text = f"The weather will go from {weatherDictionary[uniqueDescriptions[0]]}"
            for i in range(1, len(uniqueDescriptions)):
                text += f" to {uniqueDescriptions[i]}"
        self._descLabel.config(text=text)



    def _setToHours(self, event):
        hours = []
        fromHour = int(self._hour.get())

        for i in range(fromHour+1, 24):
            if i < 10:
                hour = "0" + str(i)
            else:
                hour = str(i)
            hours.append(hour)

        self._toHourChosen["values"] = hours
        self._toHourChosen.current(0)

    def _getDates(self):
        today = datetime.now().strftime("%a %d.%m")
        dates = [today]

        for i in range(1, 3):
            nextDate = (datetime.now() + timedelta(i)).strftime("%a %d.%m")
            dates.append(nextDate)

        return dates

    def _setHours(self, event):
        hours = []
        if self._day.get() == self._getDates()[0]:  # today
            thisHour = datetime.now().strftime("%H")
            hours.append(thisHour)
            for i in range(1, 24 - (int(thisHour))):
                nextHour = (datetime.now() + timedelta(hours=i)).strftime("%H")
                hours.append(nextHour)
        else:
            for i in range(24):
                hour = (datetime.now() + timedelta(hours=i)).strftime("%H")
                hours.append(hour)
            hours.sort()

        self._hourChosen["values"] = hours
        self._hourChosen.current(0)

    def _getHours(self):
        hours = []
        if self._day.get() == self._getDates()[0]: # today
            thisHour = datetime.now().strftime("%H")
            hours.append(thisHour)
            for i in range(1, 24-(int(thisHour))):
                nextHour = (datetime.now() + timedelta(hours=i)).strftime("%H")
                hours.append(nextHour)
        else:
            for i in range(24):
                hour = (datetime.now() + timedelta(hours=i)).strftime("%H")
                hours.append(hour)
            hours.sort()

        self._hourChosen["values"] = hours
        self._toHourChosen["values"] = hours



master = Tk()
myGUI = SkiWeatherGUI(master)
master.mainloop()