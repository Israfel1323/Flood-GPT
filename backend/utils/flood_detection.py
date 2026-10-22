import ee

# Initialize Earth Engine
try:
    ee.Initialize(project='floodgpt')
except:
    ee.Authenticate()
    ee.Initialize(project='floodgpt')


def detect_flood(lat, lon):
    """
    Detect flood presence using Sentinel-1 SAR
    """

    point = ee.Geometry.Point([lon, lat]).buffer(500)

    # BEFORE (dry period)
    before = ee.ImageCollection("COPERNICUS/S1_GRD") \
        .filterBounds(point) \
        .filterDate("2020-01-01", "2020-01-10") \
        .select("VV") \
        .mean()

    # AFTER (recent)
    after = ee.ImageCollection("COPERNICUS/S1_GRD") \
        .filterBounds(point) \
        .filterDate("2020-01-15", "2020-01-25") \
        .select("VV") \
        .mean()

    # Difference
    diff = before.subtract(after)

    value = diff.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=point,
        scale=30
    ).get("VV")

    if value is None:
        return False

    value = ee.Number(value).getInfo()

    # Threshold for flood detection
    return value > 1.5