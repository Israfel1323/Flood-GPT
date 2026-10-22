def analyze_route(route_coords, get_weather, get_elevation, get_ndvi, detect_flood):

    risky_points = 0
    total_checked = 0

    # ONLY CHECK FEW POINTS (FAST)
    sample_points = route_coords[::30]  # skip most points

    for lat, lon in sample_points:

        try:
            weather = get_weather(lat, lon)

            # SKIP HEAVY CALLS (THIS WAS FREEZING YOUR APP)
            elevation = get_elevation(lat, lon)

            score = weather["rainfall"] * 2

            if elevation < 450:
                score += 20

            total_checked += 1

            if score > 40:
                risky_points += 1

        except:
            continue

    if total_checked == 0:
        return "UNKNOWN", "No data"

    ratio = risky_points / total_checked

    if ratio < 0.2:
        return "SAFE", "Route is safe"
    elif ratio < 0.5:
        return "MODERATE", "Some risky areas"
    else:
        return "DANGEROUS", "Flood-prone route"