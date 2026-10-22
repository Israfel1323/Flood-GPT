import ee

def is_permanent_water(lat, lon):
    try:
        point = ee.Geometry.Point([lon, lat]).buffer(50)  # smaller buffer

        # ---------------- WATER (JRC) ----------------
        water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")

        water_mask = water.gt(40)  # stricter threshold

        water_val = water_mask.reduceRegion(
            reducer=ee.Reducer.max(),
            geometry=point,
            scale=30,
            maxPixels=1e9
        ).get("occurrence")

        water_detected = False
        if water_val is not None:
            water_detected = ee.Number(water_val).getInfo() == 1

        # ---------------- NDVI CHECK (IMPORTANT) ----------------
        s2 = ee.ImageCollection("COPERNICUS/S2") \
            .filterBounds(point) \
            .filterDate("2023-01-01", "2023-12-31") \
            .sort("CLOUDY_PIXEL_PERCENTAGE") \
            .first()

        ndvi = s2.normalizedDifference(["B8", "B4"])

        ndvi_val = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=10
        ).get("nd")

        ndvi_value = 0
        if ndvi_val:
            ndvi_value = ee.Number(ndvi_val).getInfo()

        # FINAL DECISION
        # water ONLY if:
        # 1. JRC says water
        # 2. NDVI is very low (not vegetation)
        if water_detected and ndvi_value < 0.15:
            return True

        return False

    except Exception as e:
        print("Water mask error:", e)
        return False