def analyze_route_risk(route_coords, get_weather, get_elevation):

    risky_points = 0

    total_points = 0

    # sample every 20th point (fast)

    sampled = route_coords[::20]

    for lat, lon in sampled:

        try:

            weather = get_weather(lat, lon)

            elevation = get_elevation(lat, lon)

            rainfall = weather["rainfall"]

            score = rainfall * 2

            if elevation < 450:

                score += 20

            total_points += 1

            if score > 40:

                risky_points += 1

        except:

            continue

    if total_points == 0:

        return "UNKNOWN", 0

    ratio = risky_points / total_points

    if ratio < 0.2:

        return "SAFE", ratio

    elif ratio < 0.5:

        return "MODERATE", ratio

    else:

        return "DANGEROUS", ratio