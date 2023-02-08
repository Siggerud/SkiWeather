import requests
from bs4 import BeautifulSoup

class WeatherScraper:
    def __init__(self, baseUrl, day, fromHour, toHour):
        self._baseUrl = baseUrl
        self._day = day
        self._fromHour = fromHour
        self._toHour = toHour
        self._rowTags = self._getTags()


    def _getTags(self):
        response = requests.get(self._baseUrl + f"?i={self._day}")
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        tags = soup.find_all("tr", class_="fluid-table__row")

        return tags

    def getWeatherDescriptions(self):
        weatherDesc = []
        for tag in self._rowTags:
            hour = tag.find("time").text
            if self._fromHour <= int(hour) < self._toHour:
                image = tag.find("img", alt=True)
                description = image["alt"]
                weatherDesc.append(description)

            if int(hour) >= self._toHour:
                break

        return weatherDesc

    def getTemperatures(self):
        temperatures = []
        for tag in self._rowTags:
            hour = tag.find("time").text
            if self._fromHour <= int(hour) < self._toHour:
                temp = tag.find("span", class_="temperature__degree").parent.text[:-1]
                temperatures.append(int(temp))

            if int(hour) >= self._toHour:
                break

        return temperatures

    def getWinds(self):
        winds = []

        for tag in self._rowTags:
            hour = tag.find("time").text
            if self._fromHour <= int(hour) < self._toHour:
                wind = tag.find("span", class_="wind__value").text
                winds.append(int(wind))

            if int(hour) >= self._toHour:
                break
        return winds

    def getWindGusts(self):
        windGusts = []

        for tag in self._rowTags:
            hour = tag.find("time").text
            if self._fromHour <= int(hour) < self._toHour:
                gust = tag.find("span", class_="wind__gust").text[2:-1]
                windGusts.append(int(gust))

            if int(hour) >= self._toHour:
                break
        return windGusts

    def getMinAndMaxPrecipitation(self):
        precipitationRange = [0, 0]

        for tag in self._rowTags:
            hour = tag.find("time").text
            if self._fromHour <= int(hour) < self._toHour:
                precipitations = tag.find_all("span", class_="Precipitation-module__main-sU6qN")
                if len(precipitations) != 2:
                    continue
                for index, precip in enumerate(precipitations):
                    precipitationRange[index] += float(precip.text.replace(",", "."))

            if int(hour) >= self._toHour:
                break

        return precipitationRange




"""
weatherDesc = []
temperatures = []
winds = []
windgusts = []
precipitationRange = [0, 0]

tags = soup.find_all("tr", class_="fluid-table__row")
for tag in tags[:5]:
    image = tag.find("img", alt=True)
    description = image["alt"]
    weatherDesc.append(description)

    temp = tag.find("span", class_="temperature__degree").parent.text[:-1]
    temperatures.append(int(temp))

    wind = tag.find("span", class_="wind__value").text
    winds.append(int(wind))

    gust = tag.find("span", class_="wind__gust").text[2:-1]
    windgusts.append(int(gust))

    precipitations = tag.find_all("span", class_="Precipitation-module__main-sU6qN")
    for index, precip in enumerate(precipitations):
        precipitationRange[index] += float(precip.text.replace(",", "."))

# preferable parameters
minTemp = -15
maxTemp = 5
maxWind = 7
maxGust = 10
preferableDescriptions = ["delvis skyet", "lettskyet", "skyet", "klarvær", "lett snø", "snø"]

okayToSki = True
if min(temperatures) < minTemp:
    okayToSki = False
elif max(temperatures) > maxTemp:
    okayToSki = False
elif max(winds) > maxWind:
    okayToSki = False
elif max(windgusts) > maxGust:
    okayToSki = False

for description in weatherDesc:
    if description not in preferableDescriptions:
        okayToSki = False

print(okayToSki)
print(precipitationRange)
"""