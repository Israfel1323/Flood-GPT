import ee
from datetime import datetime, timedelta

try:
    ee.Initialize(project='floodgpt')
except:
    ee.Authenticate()
    ee.Initialize(project='floodgpt')


def safe_get(value):
    try:
        if value is None:
            return 0
        return ee.Number(value).getInfo()
    except:
        return 0


def get_flood_extent_and_population(lat, lon):

    point = ee.Geometry.Point([lon, lat]).buffer(3000)

    # DYNAMIC DATE LOGIC
    today = datetime.utcnow()

    recent_start = today - timedelta(days=7)
    recent_end = today

    prev_start = today - timedelta(days=20)
    prev_end = today - timedelta(days=10)

    recent_start = recent_start.strftime("%Y-%m-%d")
    recent_end = recent_end.strftime("%Y-%m-%d")

    prev_start = prev_start.strftime("%Y-%m-%d")
    prev_end = prev_end.strftime("%Y-%m-%d")

    try:
        # BEFORE (previous period)
        before = ee.ImageCollection("COPERNICUS/S1_GRD") \
            .filterBounds(point) \
            .filterDate(prev_start, prev_end) \
            .select("VV") \
            .mean()

        # AFTER (recent period)
        after = ee.ImageCollection("COPERNICUS/S1_GRD") \
            .filterBounds(point) \
            .filterDate(recent_start, recent_end) \
            .select("VV") \
            .mean()

        # Difference
        diff = before.subtract(after)

        flood_mask = diff.gt(1.5)

        # Remove permanent water
        water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
        non_permanent = water.lt(50)

        flood_clean = flood_mask.And(non_permanent)

        # AREA calculation
        area_image = flood_clean.multiply(ee.Image.pixelArea())

        flooded_area = area_image.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=point,
            scale=30,
            maxPixels=1e9
        ).get("VV")

        flooded_area = safe_get(flooded_area) / 1e6

        # POPULATION
        population = ee.ImageCollection("WorldPop/GP/100m/pop") \
            .filterDate("2020-01-01", "2020-12-31") \
            .mean()

        affected_population = population.updateMask(flood_clean).reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=point,
            scale=100,
            maxPixels=1e9
        ).get("population")

        affected_population = safe_get(affected_population)

        return {
            "flood_area_km2": round(flooded_area, 2),
            "affected_population": int(affected_population)
        }

    except Exception as e:
        print("Flood extent error:", e)
        return {
            "flood_area_km2": 0,
            "affected_population": 0
        }