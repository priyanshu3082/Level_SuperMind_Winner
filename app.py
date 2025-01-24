import os
from dotenv import load_dotenv
import streamlit as st
import ephem  # for calculating planetary positions
from opencage.geocoder import OpenCageGeocode  # for getting latitude and longitude
import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Load environment variables
load_dotenv()
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

if not OPENCAGE_API_KEY:
    st.error("❌ OpenCage API Key is missing. Please check your .env file.")
    st.stop()

geocoder = OpenCageGeocode(OPENCAGE_API_KEY)

# Function to get latitude and longitude
def get_lat_long(city, state):
    query = f"{city}, {state}"
    results = geocoder.geocode(query)
    
    if results:
        lat = results[0]['geometry']['lat']
        lon = results[0]['geometry']['lng']
        return lat, lon
    else:
        return None, None

# Function to validate date and time format
def validate_datetime(date, time):
    try:
        datetime.datetime.combine(date, time)  # Validate date-time input
        return True
    except ValueError:
        return False

# Function to calculate planetary positions and nakshatras
def get_planet_positions(date, time, lat, lon):
    planets = {
        "Sun": ephem.Sun(),
        "Moon": ephem.Moon(),
        "Mars": ephem.Mars(),
        "Mercury": ephem.Mercury(),
        "Jupiter": ephem.Jupiter(),
        "Venus": ephem.Venus(),
        "Saturn": ephem.Saturn(),
        "Rahu": ephem.planet("Rahu"),  # Approximate Rahu manually
        "Ketu": ephem.planet("Ketu")   # Approximate Ketu manually
    }
    
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = f"{date} {time}"

    planet_positions = {}
    for name, body in planets.items():
        body.compute(obs)
        house_number = int((body.ra / (2 * ephem.pi)) * 12) + 1
        house_number = house_number if house_number <= 12 else house_number - 12
        nakshatra = ephem.constellation(body)  # Nakshatra and sign
        planet_positions[name] = {
            "house": house_number,
            "nakshatra": nakshatra[1],  # Zodiac sign
            "degrees": round(body.ra * (180 / ephem.pi), 2)  # Degrees
        }

    return planet_positions

# Function to calculate Ascendants (Lagna)
def calculate_ascendants(date, time, lat, lon):
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = f"{date} {time}"

    ascendants = {}
    for i in range(12):
        sun = ephem.Sun()
        sun.compute(obs)
        ascendant_sign = ephem.constellation(sun)[1]
        ascendants[i + 1] = ascendant_sign
        obs.date += ephem.hour * 2  # Increment time by 2 hours

    return ascendants

# Function to generate Yogas (basic examples)
def calculate_yogas(planet_positions):
    yogas = []
    if planet_positions["Jupiter"]["house"] == 9:
        yogas.append("Raja Yoga: Jupiter in the 9th house indicates good fortune and success.")
    if planet_positions["Venus"]["house"] == 7:
        yogas.append("Dhana Yoga: Venus in the 7th house signifies wealth and good relationships.")
    if planet_positions["Saturn"]["house"] == 10:
        yogas.append("Karma Yoga: Saturn in the 10th house indicates discipline and career growth.")
    if not yogas:
        yogas.append("No significant yogas identified.")
    return yogas

# Function to calculate Dasha periods (simplified)
def calculate_dasha():
    return {
        "Current Dasha": "Jupiter",
        "Next Dasha": "Saturn",
        "Following Dasha": "Mercury"
    }

# Function to suggest gemstones
def suggest_gemstones():
    return {
        "Sun": "Ruby - for vitality and confidence.",
        "Moon": "Pearl - for emotional balance.",
        "Mars": "Red Coral - for courage and strength.",
        "Mercury": "Emerald - for intelligence and communication.",
        "Jupiter": "Yellow Sapphire - for prosperity and wisdom.",
        "Venus": "Diamond - for love and beauty.",
        "Saturn": "Blue Sapphire - for discipline and focus.",
        "Rahu": "Hessonite - for overcoming obstacles.",
        "Ketu": "Cat's Eye - for spiritual growth."
    }

# Function to plot Kundli
def plot_kundli(house_labels, planets_in_houses, ascendants):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis('off')

    diamond_points = {
        1: (0, 0.6), 2: (0.3, 0.3), 3: (0.6, 0), 4: (0.3, -0.3),
        5: (0, -0.6), 6: (-0.3, -0.3), 7: (-0.6, 0), 8: (-0.3, 0.3),
        9: (0.6, 0.6), 10: (0.6, -0.6), 11: (-0.6, -0.6), 12: (-0.6, 0.6)
    }

    lines = [
        [diamond_points[1], diamond_points[9], diamond_points[3], diamond_points[10], diamond_points[1]],
        [diamond_points[5], diamond_points[10], diamond_points[7], diamond_points[11], diamond_points[5]],
        [diamond_points[1], diamond_points[8], diamond_points[7], diamond_points[12], diamond_points[1]],
        [diamond_points[3], diamond_points[9], diamond_points[11], diamond_points[6], diamond_points[3]],
    ]

    for line in lines:
        poly = Polygon(line, closed=True, edgecolor='black', fill=None, linewidth=2)
        ax.add_patch(poly)

    for house, pos in diamond_points.items():
        ax.text(pos[0], pos[1] + 0.08, house_labels.get(house, ""), fontsize=12, ha="center", va="center", fontweight="bold")
        ax.text(pos[0], pos[1] - 0.08, ascendants.get(house, ""), fontsize=10, ha="center", va="center", color="blue")

    plt.title("Vedic Kundli Chart with Ascendants", fontsize=16, fontweight="bold")
    st.pyplot(fig)

# Main function
def main():
    st.title("🔮 Kundali Generator 🔮")
    
    city = st.text_input("Enter your City:")
    state = st.text_input("Enter your State:")
    dob = st.date_input("Date of Birth")
    tob = st.time_input("Time of Birth")

    if st.button("Generate Kundali"):
        lat, lon = get_lat_long(city, state)
        if lat is None:
            st.error("❌ Unable to fetch latitude and longitude. Check city and state input.")
            return

        planet_positions = get_planet_positions(dob, tob, lat, lon)
        ascendants = calculate_ascendants(dob, tob, lat, lon)
        plot_kundli({}, {}, ascendants)

if __name__ == "__main__":
    main()
