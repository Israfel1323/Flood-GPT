from flask import Flask, request, jsonify

from flask_cors import CORS

import ee

import re

# IMPORTS

from utils.weather import get_weather

from utils.dem import get_elevation

from utils.satellite import get_ndvi, detect_flood

from utils.population import get_population

from utils.geocoding import geocode

from utils.routes import get_route

from utils.water_mask import is_permanent_water

from utils.route_risk import analyze_route_risk

app = Flask(__name__)

CORS(app)

# ---------------- INIT EARTH ENGINE ----------------

try:

    ee.Initialize(project='floodgpt')

except:

    ee.Authenticate()

    ee.Initialize(project='floodgpt')

# ---------------- FLOOD MODEL ----------------

def calculate_flood(rainfall, elevation, ndvi, sar_flood):

    score = 0

    if rainfall > 100:

        score += 40

    elif rainfall > 50:

        score += 25

    elif rainfall > 20:

        score += 10

    if elevation < 450:

        score += 20

    elif elevation < 500:

        score += 10

    if ndvi < 0.2:

        score += 10

    if sar_flood > 0.5:

        score += 30

    elif sar_flood > 0.1:

        score += 15

    if score < 20:

        return "LOW", "Minimal risk"

    elif score < 40:

        return "MEDIUM", "Waterlogging possible"

    elif score < 80:

        return "HIGH", "Urban flooding likely"

    else:

        return "VERY HIGH", "Severe flooding expected"

# ---------------- MAIN ----------------

@app.route('/chat', methods=['POST'])

def chat():

    try:

        data = request.get_json()

        message = data.get("message", "").lower()

        lat = data.get("latitude")

        lon = data.get("longitude")

        # ==================================================

        # SMART QUERY MODE

        # ==================================================

        if "mm rainfall" in message or "rainfall" in message:

            nums = re.findall(r'\d+', message)

            rain = int(nums[0]) if nums else 0

            if rain < 10:

                reply = "Very low rainfall. No flood risk."

            elif rain < 30:

                reply = "Light rainfall. Minor waterlogging possible."

            elif rain < 60:

                reply = "Moderate rainfall. Urban flooding possible."

            elif rain < 100:

                reply = "Heavy rainfall. High flood risk in low-lying areas."

            else:

                reply = "Extreme rainfall. Severe flooding expected."

            return jsonify({"reply": reply})

        if "weather" in message:

            lat_q, lon_q = 17.385, 78.4867

            weather = get_weather(lat_q, lon_q)

            rain = weather["rainfall"]

            if rain == 0:

                status = "Weather is clear and safe."

            elif rain < 20:

                status = "Light rain. Conditions are manageable."

            elif rain < 50:

                status = "Moderate rain. Be cautious."

            else:

                status = "Heavy rainfall. Flood risk increasing."

            return jsonify({

                "reply": f"Rainfall: {rain} mm. {status}"

            })

        if "optimal" in message:

            return jsonify({

                "reply": """

Optimal flood-safe conditions:

- Rainfall < 20 mm

- Elevation > 500 m

- NDVI > 0.4

- No SAR flood detection

"""

            })

        if "avoid" in message:

            return jsonify({

                "reply": """

Avoid routes that:

- Are in low elevation areas (<450m)

- Pass near lakes/rivers

- Have rainfall > 50mm

- Show SAR flood detection

"""

            })

        # ==================================================

        # ROUTE MODE

        # ==================================================

        if " to " in message:

            parts = message.split(" to ")

            if len(parts) != 2:

                return jsonify({"reply": "Use format: place1 to place2"})

            start_name = parts[0].strip()

            end_name = parts[1].strip()

            start = geocode(start_name)

            end = geocode(end_name)

            if not start or not end:

                return jsonify({"reply": "Location not found"})

            route = get_route(start, end)

            if not route:

                return jsonify({"reply": "Route not found"})

            # FAST route risk

            sampled = route["geometry"][::50]

            risky = 0

            for lat_p, lon_p in sampled:

                try:

                    weather = get_weather(lat_p, lon_p)

                    elevation = get_elevation(lat_p, lon_p)

                    if weather["rainfall"] > 20 or elevation < 450:

                        risky += 1

                except:

                    continue

            ratio = risky / len(sampled) if sampled else 0

            if ratio < 0.2:

                route_safety = "SAFE"

            elif ratio < 0.5:

                route_safety = "MODERATE"

            else:

                route_safety = "DANGEROUS"

            # 🔥 TEST MODE: FORCE ROUTE DANGER

            if "test" in message:

                print("TEST MODE ACTIVE")

                route_safety = "DANGEROUS"

            # destination analysis

            weather = get_weather(*end)

            # 🔥 TEST MODE: FORCE HEAVY RAIN

            if "test" in message:

                weather["rainfall"] = 120

            elevation = get_elevation(*end)

            # lightweight

            ndvi = 0.3

            sar = 0

            population = 1000

            risk, impact = calculate_flood(

                weather["rainfall"], elevation, ndvi, sar

            )

            alt_route = None

            if route_safety != "SAFE":

                alt_end = (end[0] + 0.02, end[1] + 0.02)

                alt_route = get_route(start, alt_end)

            return jsonify({

                "reply": f"""

Route Analysis

From: {start_name}

To: {end_name}

Distance: {route['distance']} km

Time: {route['duration']} min

Rainfall: {weather['rainfall']} mm

Elevation: {elevation} m

Risk: {risk}

Impact: {impact}

Route Safety: {route_safety}

""",

                "route": route["geometry"],

                "alt_route": alt_route["geometry"] if alt_route else None

            })

        # ==================================================

        # POINT MODE

        # ==================================================

        if lat is not None and lon is not None:

            if is_permanent_water(lat, lon):

                return jsonify({"reply": "Water body detected"})

            weather = get_weather(lat, lon)

            elevation = get_elevation(lat, lon)

            ndvi = get_ndvi(lat, lon)

            sar = detect_flood(lat, lon)

            population = get_population(lat, lon)

            risk, impact = calculate_flood(

                weather["rainfall"], elevation, ndvi, sar

            )

            return jsonify({

                "reply": f"""

Flood Analysis

Rainfall: {weather['rainfall']} mm

Elevation: {elevation} m

NDVI: {round(ndvi, 2)}

SAR Flood: {round(sar, 2)} km²

Population: {population}

Risk: {risk}

Impact: {impact}

"""

            })

        return jsonify({"reply": "Invalid request"})

    except Exception as e:

        print("ERROR:", e)

        return jsonify({"error": str(e)})

# ---------------- RUN ----------------

if __name__ == "__main__":

    app.run(debug=True)