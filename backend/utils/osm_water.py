import requests
import math


def distance(lat1, lon1, lat2, lon2):
    # simple haversine
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))


def is_water_osm(lat, lon):

    overpass_url = "http://overpass-api.de/api/interpreter"

    query = f"""
    [out:json];
    (
      way(around:200,{lat},{lon})["waterway"];
      way(around:200,{lat},{lon})["natural"="water"];
      relation(around:200,{lat},{lon})["waterway"];
      relation(around:200,{lat},{lon})["natural"="water"];
    );
    out geom;
    """

    try:
        response = requests.get(overpass_url, params={'data': query})
        data = response.json()

        for element in data.get("elements", []):

            if "geometry" in element:
                for node in element["geometry"]:

                    d = distance(lat, lon, node["lat"], node["lon"])

                    # CRITICAL: distance threshold
                    if d < 80:  # 80 meters from river
                        return True

        return False

    except Exception as e:
        print("OSM error:", e)
        return False