import requests
from bs4 import BeautifulSoup

class WeatherScraper:
    # scrapes yr.no for weather info
    def __init__(self, baseUrl, day, fromHour, duration):
        self._baseUrl = baseUrl
        self._day = day
        self._fromHour = fromHour
        self._duration = duration
        self._daysOutside = self._getDaysOutside()
        self._rowTags = self._getTags()
    
    # checks how many times we pass midnights, as we need this info when scraping
    def _getDaysOutside(self):
        if 47 >= self._fromHour + self._duration > 23:
            return 2
        elif self._fromHour + self._duration > 47:
            return 3
        return 1
    
    # retrieving tags of interest
    def _getTags(self):
        tagList = []
        for i in range(self._daysOutside):
            response = requests.get(self._baseUrl + f"?i={self._day + i}")
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            tags = soup.find_all("tr", class_="fluid-table__row")
            tagList.append(tags)

        return tagList
        
    # checking if hour count has started
    def _hourCountStarted(self, hours):
        if len(hours) == 1:
            hour = int(hours[0].text)
            if hour == self._fromHour:
                return True
        else:
            hourRange = self._getHourRange(hours)
                    
            if self._fromHour in hourRange:
                return True
                
        return False
    
    # returns value for hour count
    def _addToHourCount(self, hours, index):
        if len(hours) == 1:
            return 1
        else:
            hourRange = self._getHourRange(hours)
            # if first hour match is in a timerange, we only count the difference
            if self._day + index == 0 and self._fromHour in hourRange:
                endHourRange = hourRange[-1]
                return (endHourRange - self._fromHour) + 1
            else:
                return 6
    
    # retrieves hour range
    def _getHourRange(self, hours):
        startHour = int(hours[0].text)
        endHour = int(hours[1].text)
        # if hour range passes midnight we split the hour range
        if endHour < startHour:
            hourRange = range(startHour, 23 + 1)
        else:
            hourRange = range(startHour, endHour + 1)
            
        return hourRange
        
    # checks if there are more hour tags to check
    def _checkIfHourCountIsFinished(self, hourCount):
        if self._fromHour + self._duration + 1 - hourCount <= 0:
            return True
        return False

    # retrieves weather descriptions
    def getWeatherDescriptions(self):
        hourCountStarted = False
        weatherDesc = []
        hourCount = self._fromHour
        for index, tagSublists in enumerate(self._rowTags):
            for tag in tagSublists:
                hours = tag.find_all("time")
                if hourCountStarted == False:
                    hourCountStarted = self._hourCountStarted(hours)
                if hourCountStarted:
                    if self._checkIfHourCountIsFinished(hourCount):
                        break
                    hourCount += self._addToHourCount(hours, index)
                    image = tag.find("img", alt=True)
                    description = image["alt"]
                    weatherDesc.append(description)
                    
        return weatherDesc

    # retrieves temperatures
    def getTemperatures(self):
        hourCountStarted = False
        hourCount = self._fromHour
        temperatures = []
        for index, tagSublists in enumerate(self._rowTags):
            for tag in tagSublists:
                hours = tag.find_all("time")
                if hourCountStarted == False:
                    hourCountStarted = self._hourCountStarted(hours)
                if hourCountStarted:
                    if self._checkIfHourCountIsFinished(hourCount):
                        break
                    hourCount += self._addToHourCount(hours, index)
                    temp = tag.find("span", class_="temperature__degree").parent.text[:-1]
                    temperatures.append(int(temp))
                    
        return temperatures

    # retrieves wind values
    def getWinds(self):
        hourCountStarted = False
        hourCount = self._fromHour
        winds = []
        for index, tagSublists in enumerate(self._rowTags):
            for tag in tagSublists:
                hours = tag.find_all("time")
                if hourCountStarted == False:
                    hourCountStarted = self._hourCountStarted(hours)
                if hourCountStarted:
                    if self._checkIfHourCountIsFinished(hourCount):
                        break
                    hourCount += self._addToHourCount(hours, index)
                    wind = tag.find("span", class_="wind__value").text
                    winds.append(int(wind))
                    

        return winds
    
    # retrieves wind gust values
    def getWindGusts(self):
        gustsFinished = False
        hourCountStarted = False
        hourCount = self._fromHour
        windGusts = []
        for index, tagSublists in enumerate(self._rowTags):
            if gustsFinished:
                break
            for tag in tagSublists:
                hours = tag.find_all("time")
                if hourCountStarted == False:
                    hourCountStarted = self._hourCountStarted(hours)
                if hourCountStarted:
                    if self._checkIfHourCountIsFinished(hourCount):
                        break
                    hourCount += self._addToHourCount(hours, index)
                    gust = tag.find("span", class_="wind__gust")
                    # yr.no only has gust values for a few days
                    if gust == None:
                        gustsFinished = True
                        break
                    else:
                        gust = gust.text[2:-1]
                    windGusts.append(int(gust))

        return windGusts
    
    # retrieves precipitation values for snow, sleet and rain
    def getMinAndMaxPrecipitation(self):
        hourCountStarted = False
        hourCount = self._fromHour
        precipitationRange = [[0, 0], [0, 0], [0, 0]] # snow, sleet, rain
        
        # for identifying the type of precipitation
        rainDescriptions = ["lett regn", "regn", "kraftig regn"]
        sleetDescriptions = ["lett sludd", "sludd", "kraftig sludd"]
        snowDescriptions = ["lett snø", "snø", "kraftig snø"]

        for index, tagSublists in enumerate(self._rowTags):
            for tag in tagSublists:
                hours = tag.find_all("time")
                if hourCountStarted == False:
                    hourCountStarted = self._hourCountStarted(hours)
                if hourCountStarted:
                    if self._checkIfHourCountIsFinished(hourCount):
                        break
                    hourCount += self._addToHourCount(hours, index)
                    precipitations = tag.find_all("span", class_="Precipitation-module__main-sU6qN")
                    if len(precipitations) != 2:
                        continue
                    image = tag.find("img", alt=True)
                    description = image["alt"]
                    
                    # check weather description to identify type of precipitation
                    if description in snowDescriptions:
                        categoryIndex = 0
                    elif description in sleetDescriptions:
                        categoryIndex = 1
                    elif description in rainDescriptions:
                        categoryIndex = 2
                    else:
                        # if no identifying weather description we base precipitation on temperature
                        temp = int(tag.find("span", class_="temperature__degree").parent.text[:-1])
                        if temp < 0:
                            categoryIndex = 0
                        elif temp == 0:
                            categoryIndex = 1
                        elif temp > 0:
                            categoryIndex = 2
                    
                    # add precipitation to lists
                    for index, precip in enumerate(precipitations):
                        # if last entry is in an hour range, we only take a fraction of the precipitation
                        if self._fromHour + self._duration - hourCount < 0:
                            fraction = (6-abs(self._fromHour + self._duration - hourCount))/6
                        else:
                            fraction = 1
                        precipitationRange[categoryIndex][index] += (float(precip.text.replace(",", ".")) * fraction)

        return precipitationRange