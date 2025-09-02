import requests
import pandas as pd
import streamlit as st
import time

# Initialize API usage counters
if "geocode_calls" not in st.session_state:
    st.session_state.geocode_calls = 0
if "nearby_calls" not in st.session_state:
    st.session_state.nearby_calls = 0
if "details_calls" not in st.session_state:
    st.session_state.details_calls = 0


API_KEY = st.secrets.get("GOOGLE_API_KEY")


# ------------------ Category → Subcategories ------------------
categories = {
    "Automotive": [
        "car_dealer", "car_rental", "car_repair", "car_wash", "electric_vehicle_charging_station","gas_station", "parking", "rest_stop"
    ],

    "Business": [
        "corporate_office", "farm", "ranch"
    ],

    "Food & Drink": [
        "restaurant", "cafe", "bakery", "bar", "meal_takeaway",
        "meal_delivery"
    ],

    "Culture": [
        "art_gallery", "art_studio", "auditorium", "cultural_landmark", "historical_place",
        "monument", "museum", "performing_arts_theater", "sculpture"
    ],

    "Education": [
        "library", "preschool", "primary_school", "school", "secondary_school", "university"
    ],

    "Entertainment & Recreation": [
    "adventure_sports_center", "amphitheatre", "amusement_center", "amusement_park",
    "aquarium", "banquet_hall", "barbecue_area", "botanical_garden", "bowling_alley", "casino",
    "children’s_camp", "comedy_club", "community_center", "concert_hall", "convention_center",
    "cultural_center", "cycling_park", "dance_hall", "dog_park", "event_venue", "ferris_wheel",
    "garden", "hiking_area", "historical_landmark", "internet_cafe", "karaoke", "marina",
    "movie_rental", "movie_theater", "national_park", "night_club", "observation_deck",
    "park", "picnic_ground", "planetarium", "plaza", "roller_coaster", "skateboard_park",
    "state_park", "tourist_attraction", "video_arcade", "visitor_center", "water_park",
    "wedding_venue", "wildlife_park", "wildlife_refuge", "zoo"

    ],

    "Facilities": [
        "public_bath", "public_bathroom", "stable"
    ],

    "Finance": [
        "accounting", "atm", "bank"
    ],

    "Food & Drink": [
    "cafe", "cafeteria", "candy_store", "chocolate_factory",
    "chocolate_shop", "coffee_shop", "tea_house",
    "restaurant"
    ],

    "Geographical Areas": [
        "administrative_area_level_1", "administrative_area_level_2", "country", "locality",
        "postal_code", "school_district"
    ],
    
    "Government": [
        "city_hall", "courthouse", "embassy", "fire_station", "government_office",
        "local_government_office", "police", "post_office"
    ],

    "Health & Wellness": [
        "chiropractor", "dental_clinic", "dentist", "doctor", "drugstore", "hospital",
        "medical_lab", "massage", "pharmacy", "physiotherapist", "sauna", "skin_care_clinic",
        "spa", "tanning_studio", "wellness_center", "yoga_studio"
    ],


    "Housing": [
        "apartment_building", "apartment_complex", "condominium_complex", "housing_complex"
    ],

    "Lodging": [
        "bed_and_breakfast", "budget_japanese_inn", "campground", "camping_cabin", "cottage",
        "extended_stay_hotel", "farmstay", "guest_house", "hostel", "hotel", "inn", "japanese_inn",
        "lodging", "mobile_home_park", "motel", "private_guest_room", "resort_hotel", "rv_park"
    ],

    "Natural Features": [
        "beach"
    ],

    "Places of Worship": [
        "church", "mosque", "synagogue", "hindu_temple"
    ],

    "Services": [
        "astrologer", "barber_shop", "beautician", "beauty_salon", "body_art_service",
        "catering_service", "cemetery", "child_care_agency", "consultant", "courier_service",
        "electrician", "florist", "food_delivery", "foot_care", "funeral_home", "hair_care",
        "hair_salon", "insurance_agency", "laundry", "lawyer", "locksmith", "makeup_artist",
        "moving_company", "nail_salon", "painter", "plumber", "psychic", "real_estate_agency",
        "roofing_contractor", "storage", "summer_camp_organizer", "tailor",
        "telecommunications_service_provider", "tour_agency", "tourist_information_center",
        "travel_agency", "veterinary_care"
    ],

    "Shopping": [
        "asian_grocery_store", "auto_parts_store", "bicycle_store", "book_store", "butcher_shop",
        "cell_phone_store", "clothing_store", "convenience_store", "department_store",
        "discount_store", "electronics_store", "food_store", "furniture_store", "gift_shop",
        "grocery_store", "hardware_store", "home_goods_store", "home_improvement_store",
        "jewelry_store", "liquor_store", "market", "pet_store", "shoe_store", "shopping_mall",
        "sporting_goods_store", "store", "supermarket", "warehouse_store", "wholesaler"
    ],

    "Sports": [
        "arena", "athletic_field", "fitness_center", "golf_course", "gym", "ice_skating_rink",
        "playground", "ski_resort", "sports_activity_location", "sports_club",
        "sports_coaching", "sports_complex", "stadium", "swimming_pool"
    ],

    "Transportation": [
        "airport", "airstrip", "bus_station", "bus_stop", "ferry_terminal", "heliport",
        "international_airport", "light_rail_station", "park_and_ride", "subway_station",
        "taxi_stand", "train_station", "transit_depot", "transit_station", "truck_stop"
    ]
}


# ------------------ Helper Functions ------------------
def geocode_address(address):
    st.session_state.geocode_calls += 1  # count usage
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": API_KEY}
    response = requests.get(url, params=params).json()
    if response['results']:
        location = response['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None


def get_nearby_places(lat, lng, radius, place_type=None, keyword=None):
    st.session_state.nearby_calls += 1  # count usage
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "key": API_KEY
    }
    if place_type:
        params["type"] = place_type
    if keyword:
        params["keyword"] = keyword

    all_results = []
    while True:
        response = requests.get(url, params=params).json()
        results = response.get('results', [])
        all_results.extend(results)

        next_page_token = response.get("next_page_token")
        if not next_page_token:
            break

        # Google requires a short delay before next_page_token becomes valid
        import time
        time.sleep(2)
        params = {"pagetoken": next_page_token, "key": API_KEY}

    return all_results[:60]  # Google max = 60 results


def get_place_details(place_id):
    st.session_state.details_calls += 1  # count usage
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": (
            "name,formatted_address,formatted_phone_number,"
            "international_phone_number,types,website,"
            "rating,user_ratings_total,"
            "opening_hours,business_status"
        ),
        "key": API_KEY
    }
    response = requests.get(url, params=params).json()
    return response.get('result', {})

# ------------------ Streamlit UI ------------------
st.title("Nearby Business Finder")

st.info(
    "For best results, please enter a full address with **city and country (United Kingdom)**. "
    "Example: *221B Baker Street, London, UK*. This ensures accurate location and nearby search results."
)

address = st.text_input("Enter Address")
radius = st.number_input("Enter Radius in meters", value=500)

category = st.selectbox("Select Category", [""] + list(categories.keys()))
subcategory = None
if category:
    subcategory = st.selectbox("Select Subcategory", [""] + categories[category])

keyword_input = st.text_input("Or enter a custom keyword (optional)")

if st.button("Search"):
    lat, lng = geocode_address(address)
    if lat and lng:
        businesses = get_nearby_places(lat, lng, radius, place_type=subcategory or None, keyword=keyword_input or None)

        if not businesses:
            st.error(f'No results found. Please try a different category, subcategory, or keyword.')
        else:
            all_data = []
            for b in businesses:
                place_id = b['place_id']
                details = get_place_details(place_id)
                # Flatten opening hours
                opening_hours = None
                if details.get("opening_hours") and "weekday_text" in details["opening_hours"]:
                    opening_hours = "; ".join(details["opening_hours"]["weekday_text"])

                all_data.append({
                "Name": details.get("name"),
                "Type": ", ".join(details.get("types", [])),
                "Address": details.get("formatted_address"),
                "Phone": details.get("formatted_phone_number"),
                "Intl Phone": details.get("international_phone_number"),
                "Website": details.get("website"),
                "Rating": details.get("rating"),
                "Total Reviews": details.get("user_ratings_total"),
                "Business Status": details.get("business_status"),
                "Opening Hours": opening_hours,
            })

            df = pd.DataFrame(all_data)
            st.dataframe(df)

            # Download Excel
            file_path = "nearby_businesses.xlsx"
            df.to_excel(file_path, index=False)
            with open(file_path, "rb") as f:
                st.download_button("Download Excel", f, file_name="businesses.xlsx")
    else:
        st.error("Could not find location for the given address.")

# ------------------- API Usage Sidebar -------------------
st.sidebar.title("API Usage Stats")
st.sidebar.write(f"Geocode API Calls: {st.session_state.geocode_calls}")
st.sidebar.write(f"Nearby Search API Calls: {st.session_state.nearby_calls}")
st.sidebar.write(f"Place Details API Calls: {st.session_state.details_calls}")

# Estimate API cost (based on Google pricing)
estimated_cost = (
    st.session_state.geocode_calls * 0.005 +
    st.session_state.nearby_calls * 0.032 +
    st.session_state.details_calls * 0.017
)
st.sidebar.write(f"Estimated Cost: ${estimated_cost:.2f}")
#st.sidebar.caption("Google Maps gives $200 free per month.\nYou'll only be charged after exceeding that.")