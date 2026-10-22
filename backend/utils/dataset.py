import pandas as pd
import random
from utils.weather import get_weather
from utils.satellite import get_satellite_features
import os


def generate_dataset(num_samples=50):
    data = []

   
    os.makedirs("data", exist_ok=True)

    for i in range(num_samples):
        print(f"Generating sample {i+1}/{num_samples}")

        #Hyderabad city coordinates
        lat = 17.2 + random.uniform(0, 0.4)
        lon = 78.2 + random.uniform(0, 0.5)

        #Weather data
        weather = get_weather(lat, lon)

        #Satellite data
        sat = get_satellite_features(lat, lon)

        rainfall = weather["rainfall"]
        temp = weather["temperature"]
        humidity = weather["humidity"]

        sar = sat["sar_water"]
        ndvi = sat["ndvi"]

        #Flood prediction logic
        flood = 1 if (rainfall > 10 or (sar == 1 and ndvi < 0.2)) else 0

        data.append({
            "latitude": lat,
            "longitude": lon,
            "rainfall": rainfall,
            "temperature": temp,
            "humidity": humidity,
            "ndvi": ndvi,
            "sar_water": sar,
            "flood": flood
        })

    df = pd.DataFrame(data)

    #path
    df.to_csv("data/dataset.csv", index=False)

    print("\nDataset saved to backend/data/dataset.csv")

    return df