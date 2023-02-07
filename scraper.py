import requests
from bs4 import BeautifulSoup

response = requests.get("https://www.yr.no/nb/v%C3%A6rvarsel/timetabell/1-305409/Norge/Troms%20og%20Finnmark/Troms%C3%B8/Troms%C3%B8?i=0")
response.raise_for_status()

weatherDesc = []
temperatures = []
winds = []
windgusts = []
precipitationRange = [0, 0]


soup = BeautifulSoup(response.content, "html.parser")
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
