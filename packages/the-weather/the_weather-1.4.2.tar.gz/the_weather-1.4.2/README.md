[![Generic badge](https://img.shields.io/badge/Licence-MIT-blue.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/Maintained-yes-green.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/Python-3.7-yellow.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/the_weather-1.4.2-red.svg)](https://pypi.org/project/the-weather/)

## Package
Package for getting weather data using a zipcode

## Usage
```python
from the_weather import *

weather = Weather(22025)

d = weather.daily_forecast("2023-09-17")
print(d[0])

# Output
Sunday 2023-09-17 [05:00 PM] - 19° 50: Scattered Showers

```
