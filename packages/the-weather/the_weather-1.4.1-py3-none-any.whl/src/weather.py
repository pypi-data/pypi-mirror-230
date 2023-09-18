import requests
from datetime import datetime

class Weather:
    def __init__(self, zipcode):
        url = f"https://www.whsv.com/pf/api/v3/content/fetch/wx-current-conditions-v3?query={{'zipCode':'{zipcode}'}}&arc-site=whsv&_website=whsv"
        res = requests.get(url)
        data = res.json()['metric']
        self.forecast = data['hourlyForecast']
        self.days = []

        self.__get_forecast()


    def __get_forecast(self):
        for i in self.forecast:
            date = i['validTimeLocal'].split('T')[0]
            time = i['validTimeLocal'].split('T')[1].split('-')[0][:5]
            t = datetime.strptime(time, "%H:%M")
            time = t.strftime("%I:%M %p")

            self.days.append(Forecast(date, i['dayOfWeek'], time, i['precipChance'], i['temperature'], i['wxPhraseLong']))

    def daily_forecast(self, date):
        items = []
        for forecast in self.days:
            if forecast.date == date:
                items.append(forecast)
        return items
    
    def get_all(self):
        return self.days

class Forecast:
    def __init__(self, date, day, time, precip, temp, desc):
        self.date = date
        self.time = time
        self.precip = precip
        self.temp = temp
        self.desc = desc
        self.day = day
    

    def __str__(self):
        return f"{self.day} {self.date} [{self.time}] - {self.temp}\xb0 {self.precip}: {self.desc}"
    
    def __repr__(self):
        return f"{self.day} {self.date} [{self.time}] - {self.temp}\xb0 {self.precip}: {self.desc}"