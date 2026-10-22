import requests

def get_route(start, end):
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"

        response = requests.get(url).json()

        route = response["routes"][0]

        coords = route["geometry"]["coordinates"]

        # convert [lon, lat] → [lat, lon]
        geometry = [[c[1], c[0]] for c in coords]

        distance = route["distance"] / 1000
        duration = route["duration"] / 60

        return {
            "geometry": geometry,
            "distance": round(distance, 2),
            "duration": round(duration, 2)
        }

    except Exception as e:
        print("Route error:", e)
        return None