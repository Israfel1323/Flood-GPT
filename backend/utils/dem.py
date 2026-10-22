import ee

try:
    ee.Initialize(project='floodgpt')
except:
    ee.Authenticate()
    ee.Initialize(project='floodgpt')


def get_elevation(lat, lon):

    point = ee.Geometry.Point([lon, lat])

    try:
        dem = ee.Image("USGS/SRTMGL1_003")

        value = dem.sample(point, 30).first()

        if value is None:
            return 0

        val = value.get("elevation")

        if val is None:
            return 0

        return ee.Number(val).getInfo()

    except Exception as e:
        print("DEM error:", e)
        return 0