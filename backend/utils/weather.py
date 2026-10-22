import requests

import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

        response = requests.get(url).json()

        print("Weather API:", response)  # debug

        rainfall = 0

        if "rain" in response:
            if "1h" in response["rain"]:
                rainfall = response["rain"]["1h"]
            elif "3h" in response["rain"]:
                rainfall = response["rain"]["3h"] / 3

        return {
            "rainfall": rainfall,
            "temperature": response["main"]["temp"],
            "humidity": response["main"]["humidity"]
        }

    except Exception as e:
        print("Weather error:", e)

        return {
            "rainfall": 0,
            "temperature": 30,
            "humidity": 50
        }