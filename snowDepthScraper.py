import requests
from bs4 import BeautifulSoup
import re

class SnowDepthScraper:
    # scrapes skiforeningen.no for snow depths info
    def __init__(self, url, place):
        self._url = url
        self._place = place
        self._tag = self._getTag()
        
    # get tag with relevant info
    def _getTag(self):
        response = requests.get(self._url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        tag = soup.find(class_="row marginBottom")
        
        return tag
    
    # get info about snow depth, update date and possible alternate location
    def getInfo(self):
        snowDepth = ""
        infoList = []
        placeFound = False
        alternatePlaceFound = False
        placesTags = self._tag.find_all("h3")
        infoTag = None
        for placeTag in placesTags:
            searchPlace = placeTag.text.split()[0]
            # check if place is the one that is selected in GUI
            if searchPlace == self._place:
                placeFound = True
                infoTag = placeTag
                break
        
        # if place is not found, we try to get an alternate location at same site
        if placeFound == False:
            for placeTag in placesTags:
                sentence = placeTag.text
                if re.search("^[a-zA-Z]+ - \d+\. [a-z]+ \d{4} kl\. \d\d:\d\d", sentence):
                    infoTag = placeTag
                    alternatePlaceFound = True
                    break
                    
        if placeFound or alternatePlaceFound:
            table = infoTag.find_next("table")
            tds = table.find_all("td")
            for td in tds:
                if td.text == "Snødybde:":
                    snowDepth = td.find_next().text.split("cm")[0].strip() + "cm"
       
            wordsOfInterest = infoTag.text.split()
            day = wordsOfInterest[2].split(".")[0]
            month, year = wordsOfInterest[3:5]
            time = wordsOfInterest[-1]
            if alternatePlaceFound:
                # providing name of alternate place if original place could not be found
                alternatePlace = wordsOfInterest[0]
            else:
                alternatePlace = ""
            infoList = [snowDepth, [day, month, year], alternatePlace]
        
        return infoList
                
        
         
                
       