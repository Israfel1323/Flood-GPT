from utils.weather import get_weather

# Tokyo coordinates (you can change later)
lat = 35.6762
lon = 139.6503

weather = get_weather(lat, lon)

print("Weather Data:", weather)