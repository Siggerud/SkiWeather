from tkinter import Tk, Label, ttk, StringVar
from datetime import datetime, timedelta

class SkiWeatherGUI:
    def __init__(self, master):
        self._master = master
        self._master.title("Ski weather checker")
        self._master.geometry("350x500")

        self._day = StringVar()
        dayChosen = ttk.Combobox(master, width=10, textvariable= self._day)
        dayChosen["values"] = self._getDates()
        dayChosen.grid(row=1, column=1)
        dayChosen.current()

        self._hour = StringVar()
        self._hourChosen = ttk.Combobox(master, width=10, textvariable= self._hour)
        self._getHours()
        self._hourChosen.grid(row=1, column=2)
        self._hourChosen.current()

        dayChosen.bind("<<ComboboxSelected>>", self._setHours)

    def setToHours(self, event):
        hours = []

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



master = Tk()
myGUI = SkiWeatherGUI(master)
master.mainloop()