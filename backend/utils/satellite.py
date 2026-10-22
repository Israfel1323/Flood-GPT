import ee

# ---------------- NDVI (Sentinel-2) ----------------
def get_ndvi(lat, lon):
    try:
        point = ee.Geometry.Point([lon, lat])

        image = ee.ImageCollection("COPERNICUS/S2_HARMONIZED") \
            .filterBounds(point) \
            .filterDate("2023-01-01", "2023-12-31") \
            .sort("CLOUDY_PIXEL_PERCENTAGE") \
            .first()

        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

        value = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=10
        ).get("NDVI")

        return round(ee.Number(value).getInfo(), 3)

    except Exception as e:
        print("NDVI error:", e)
        return 0


# ---------------- SAR FLOOD (Sentinel-1) ----------------
def detect_flood(lat, lon):
    try:
        point = ee.Geometry.Point([lon, lat]).buffer(500)

        before = ee.ImageCollection("COPERNICUS/S1_GRD") \
            .filterBounds(point) \
            .filterDate("2023-01-01", "2023-06-01") \
            .select("VV") \
            .mean()

        after = ee.ImageCollection("COPERNICUS/S1_GRD") \
            .filterBounds(point) \
            .filterDate("2023-06-01", "2023-12-31") \
            .select("VV") \
            .mean()

        diff = after.subtract(before)

        flood = diff.lt(-1.5)  # threshold

        flooded_area = flood.multiply(ee.Image.pixelArea()).reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=point,
            scale=10
        ).get("VV")

        flooded_area_km2 = ee.Number(flooded_area).divide(1e6)

        return round(flooded_area_km2.getInfo(), 2)

    except Exception as e:
        print("SAR error:", e)
        return 0