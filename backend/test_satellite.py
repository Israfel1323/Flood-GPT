from utils.satellite import get_satellite_features

lat = 35.6762
lon = 139.6503

data = get_satellite_features(lat, lon)

print("\nFINAL SATELLITE DATA:", data)