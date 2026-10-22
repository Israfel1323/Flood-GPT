import ee

def get_population(lat, lon):

    try:

        point = ee.Geometry.Point([lon, lat])

        # FIXED DATASET

        pop = ee.ImageCollection("WorldPop/GP/100m/pop") \
            .filterDate("2020-01-01", "2020-12-31") \
            .first()

        value = pop.reduceRegion(

            reducer=ee.Reducer.mean(),

            geometry=point,

            scale=100

        ).getInfo()

        return int(list(value.values())[0])

    except Exception as e:

        print("Population error:", e)

        return 1000  # fallback