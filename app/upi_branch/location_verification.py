import os
from opencage.geocoder import OpenCageGeocode
from urllib.parse import parse_qs

OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
geocoder = OpenCageGeocode(OPENCAGE_API_KEY)


def extract_merchant_address(upi_id: str, merchant_db) -> str:
    """
    Looks up the registered address of a merchant from the merchant database.
    Assumes merchant_database.csv has an 'address' column for fixed shops.
    """
    match = merchant_db[merchant_db["upi_id"] == upi_id]
    if not match.empty and "address" in match.columns:
        return match.iloc[0]["address"]
    return None


def geocode_address(address: str):
    """
    Converts a text address into (lat, lng) using OpenCage.
    Returns None if geocoding fails.
    """
    try:
        results = geocoder.geocode(address)
        if results and len(results) > 0:
            lat = results[0]["geometry"]["lat"]
            lng = results[0]["geometry"]["lng"]
            return (lat, lng)
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None


def haversine_distance(coord1, coord2) -> float:
    """
    Calculates distance in km between two (lat, lng) points.
    """
    from math import radians, sin, cos, sqrt, atan2

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    R = 6371 # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def verify_location(payload: str, merchant_db, user_lat: float = None, user_lng: float = None,
                     is_fixed_shop: bool = True, max_distance_km: float = 1.0) -> dict:
    """
    Verifies that the scan location matches the merchant's registered
    location. Only applies to fixed shop merchants.

    Returns:
        dict: {
            "applicable": bool,
            "match": bool or None,
            "distance_km": float or None
        }
    """
    if not is_fixed_shop:
        return {"applicable": False, "match": None, "distance_km": None}

    if user_lat is None or user_lng is None:
        return {"applicable": True, "match": None, "distance_km": None}

    query_string = payload.split("?", 1)[-1] if "?" in payload else ""
    params = parse_qs(query_string)
    upi_id = params.get("pa", [None])[0]

    merchant_address = extract_merchant_address(upi_id, merchant_db)
    if not merchant_address:
        return {"applicable": True, "match": None, "distance_km": None}

    merchant_coords = geocode_address(merchant_address)
    if merchant_coords is None:
        return {"applicable": True, "match": None, "distance_km": None}

    distance = haversine_distance((user_lat, user_lng), merchant_coords)
    is_match = distance <= max_distance_km

    return {"applicable": True, "match": is_match, "distance_km": round(distance, 2)}

