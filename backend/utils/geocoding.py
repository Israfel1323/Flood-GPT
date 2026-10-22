import requests

def geocode(place):

    try:

        url = "https://nominatim.openstreetmap.org/search"

        params = {

            "q": place,

            "format": "json",

            "limit": 3,

            "addressdetails": 1

        }

        headers = {

            "User-Agent": "flood-gpt"

        }

        response = requests.get(url, params=params, headers=headers).json()

        if not response:

            return None

        # PRIORITY FILTER: Hyderabad

        for r in response:

            address = r.get("address", {})

            if (

                "hyderabad" in str(address).lower() or

                "telangana" in str(address).lower()

            ):

                return (float(r["lat"]), float(r["lon"]))

        # fallback → first result

        r = response[0]

        return (float(r["lat"]), float(r["lon"]))

    except:

        return None