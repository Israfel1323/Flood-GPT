import random

import pandas as pd

def calculate_flood(rainfall, elevation, ndvi, sar_flood):

    score = 0

    # rainfall

    if rainfall > 100:

        score += 40

    elif rainfall > 50:

        score += 25

    elif rainfall > 20:

        score += 10

    # elevation

    if elevation < 450:

        score += 20

    elif elevation < 500:

        score += 10

    # vegetation

    if ndvi < 0.2:

        score += 10

    # SAR flood

    if sar_flood > 0.5:

        score += 30

    elif sar_flood > 0.1:

        score += 15

    # classification

    if score < 20:

        return "LOW"

    elif score < 40:

        return "MEDIUM"

    elif score < 80:

        return "HIGH"

    else:

        return "VERY HIGH"

data = []

# 🔥 Generate 15,000 rows

for i in range(15000):

    rainfall = random.randint(0, 200)              # mm

    elevation = random.randint(300, 700)           # meters

    ndvi = round(random.uniform(0, 0.8), 2)        # vegetation index

    sar_flood = round(random.uniform(0, 1), 2)     # flood area

    risk = calculate_flood(rainfall, elevation, ndvi, sar_flood)

    data.append([

        rainfall,

        elevation,

        ndvi,

        sar_flood,

        risk

    ])

df = pd.DataFrame(data, columns=[

    "rainfall",

    "elevation",

    "ndvi",

    "sar_flood",

    "risk"

])

# save file

df.to_csv("dataset.csv", index=False)

print("Dataset generated successfully with", len(df), "records")