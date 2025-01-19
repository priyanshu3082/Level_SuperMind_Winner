import os
from dotenv import OPENCAGE_API_KEY
import streamlit as st
import ephem  # for calculating planetary positions
from opencage.geocoder import OpenCageGeocode  # for getting latitude and longitude
import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# OpenCage API Key (Replace with your key)


# Function to get latitude and longitude
def get_lat_long(city, state):
    geocoder = OpenCageGeocode(os.getenv(OPENCAGE_API_KEY))
    query = f"{city}, {state}"
    results = geocoder.geocode(query)
    
    if results:
        lat = results[0]['geometry']['lat']
        lon = results[0]['geometry']['lng']
        return lat, lon
    else:
        return None, None

# Function to validate date and time format
def validate_datetime(date_str, time_str):
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")  # Validate date
        datetime.datetime.strptime(time_str, "%H:%M:%S")  # Validate time
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
        "Rahu": ephem.Neptune(),  # Approximation for Rahu
        "Ketu": ephem.Uranus()    # Approximation for Ketu
    }
    
    datetime_str = f"{date} {time}"
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = ephem.Date(datetime_str)

    planet_positions = {}
    for name, body in planets.items():
        body.compute(obs)
        # Calculate house position based on right ascension (RA)
        house_number = int((body.ra / (2 * ephem.pi)) * 12) + 1
        house_number = house_number if house_number <= 12 else house_number - 12
        nakshatra = ephem.constellation(body)  # Nakshatra and sign
        planet_positions[name] = {
            "house": house_number,
            "nakshatra": nakshatra[1],  # Zodiac sign
            "degrees": round(body.ra * (180 / ephem.pi), 2)  # Degrees
        }

    return planet_positions

# Function to determine all Ascendants (Lagna) based on time
def calculate_ascendants(date, time, lat, lon):
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = ephem.Date(f"{date} {time}")

    # Ascendant changes approximately every 2 hours, loop through all 12 signs
    ascendants = {}
    for i in range(12):
        sun = ephem.Sun()
        sun.compute(obs)
        ascendant_sign = ephem.constellation(sun)[1]
        ascendants[i + 1] = ascendant_sign
        obs.date += ephem.hour * 2  # Increment time by 2 hours

    return ascendants

# Function to generate Yogas (simple examples)
def calculate_yogas(planet_positions):
    yogas = []

    # Example Yogas (you can add more complex rules)
    if "Jupiter" in planet_positions and planet_positions["Jupiter"]["house"] == 9:
        yogas.append("Raja Yoga: Jupiter in the 9th house indicates good fortune and success.")

    if "Venus" in planet_positions and planet_positions["Venus"]["house"] == 7:
        yogas.append("Dhana Yoga: Venus in the 7th house signifies wealth and good relationships.")

    if "Saturn" in planet_positions and planet_positions["Saturn"]["house"] == 10:
        yogas.append("Karma Yoga: Saturn in the 10th house indicates discipline and career growth.")

    if not yogas:
        yogas.append("No significant yogas identified.")
    
    return yogas

# Function to display Dasha Periods (simplified)
def calculate_dasha():
    return {
        "Current Dasha": "Jupiter",
        "Next Dasha": "Saturn",
        "Following Dasha": "Mercury"
    }

# Function to suggest gemstones based on planetary positions
def suggest_gemstones(planet_positions):
    gemstones = {
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
    
    suggested_gemstones = {}
    for planet, details in planet_positions.items():
        suggested_gemstones[planet] = gemstones.get(planet, "No gemstone suggestion available.")
    
    return suggested_gemstones

# Function to recommend Poojas (rituals)
def recommend_poojas(planet_positions):
    poojas = {
        "Sun": "Perform Surya Namaskar and offer water to the Sun in the morning.",
        "Moon": "Chant Chandra Mantra and offer rice and milk to the Moon.",
        "Mars": "Perform Mangal Dosh Nivaran Pooja on Tuesdays.",
        "Mercury": "Recite Budh Mantra and offer green gram to Lord Ganesha.",
        "Jupiter": "Conduct a Guru Pooja and offer yellow flowers.",
        "Venus": "Perform Lakshmi Pooja on Fridays.",
        "Saturn": "Chant Shani Mantra and offer black sesame seeds on Saturdays.",
        "Rahu": "Recite Rahu Mantra and offer black gram.",
        "Ketu": "Perform Ketu Pooja and offer coconut."
    }
    
    recommended_poojas = {}
    for planet, details in planet_positions.items():
        recommended_poojas[planet] = poojas.get(planet, "No Pooja recommendation available.")
    
    return recommended_poojas

# Function to provide Do's and Don'ts based on planetary positions
def dos_and_donts(planet_positions):
    dos = []
    donts = []

    if "Jupiter" in planet_positions and planet_positions["Jupiter"]["house"] == 9:
        dos.append("Engage in spiritual practices and charity.")
    else:
        donts.append("Avoid excessive pride and arrogance.")

    if "Venus" in planet_positions and planet_positions["Venus"]["house"] == 7:
        dos.append("Nurture relationships and focus on creativity.")
    else:
        donts.append("Avoid superficial relationships.")

    if "Saturn" in planet_positions and planet_positions["Saturn"]["house"] == 10:
        dos.append("Work hard and be disciplined in your career.")
    else:
        donts.append("Avoid laziness and procrastination.")

    return dos, donts

# Function to generate personalized spiritual guidance
def spiritual_guidance(planet_positions):
    guidance = []
    if "Moon" in planet_positions:
        guidance.append("Focus on emotional well-being and meditation.")
    if "Mars" in planet_positions:
        guidance.append("Channel your energy into physical activities.")
    if "Jupiter" in planet_positions:
        guidance.append("Seek knowledge and wisdom through study.")
    
    return guidance

# Function to plot the square Kundli chart with Ascendants
def plot_kundli(house_labels, planets_in_houses, ascendants):
    # Set up the plot
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis('off')

    # Define the key points for the diamond layout
    diamond_points = {
        1: (0, 0.6), 2: (0.3, 0.3), 3: (0.6, 0), 4: (0.3, -0.3),
        5: (0, -0.6), 6: (-0.3, -0.3), 7: (-0.6, 0), 8: (-0.3, 0.3),
        9: (0.6, 0.6), 10: (0.6, -0.6), 11: (-0.6, -0.6), 12: (-0.6, 0.6)
    }

    # Connect points to form houses
    lines = [
        [diamond_points[1], diamond_points[9], diamond_points[3], diamond_points[10], diamond_points[1]],  # Top
        [diamond_points[5], diamond_points[10], diamond_points[7], diamond_points[11], diamond_points[5]],  # Bottom
        [diamond_points[1], diamond_points[8], diamond_points[7], diamond_points[12], diamond_points[1]],  # Left
        [diamond_points[3], diamond_points[9], diamond_points[11], diamond_points[6], diamond_points[3]],  # Right
    ]

    # Draw the diamond shapes for the grid
    for line in lines:
        poly = Polygon(line, closed=True, edgecolor='black', fill=None, linewidth=2)
        ax.add_patch(poly)

    # Add house numbers and ascendants to the chart
    for house, pos in diamond_points.items():
        ax.text(pos[0], pos[1] + 0.08, house_labels.get(house, ""), fontsize=12, ha="center", va="center", fontweight="bold")
        ax.text(pos[0], pos[1] - 0.08, ascendants.get(house, ""), fontsize=10, ha="center", va="center", color="blue")

    # Add planets in their respective houses
    for planet, house in planets_in_houses.items():
        pos = diamond_points[house]
        ax.text(pos[0], pos[1] - 0.15, planet, fontsize=10, ha="center", va="center", color="red")

    plt.title("Vedic Kundli Chart with Ascendants", fontsize=16, fontweight="bold")
    st.pyplot(fig)  # Use Streamlit to display the plot

# Main program
def main():
    st.title("🔮 Kundali Generator 🔮")
    
    name = st.text_input("Enter your name:")
    dob = st.date_input("Enter your Date of Birth (YYYY-MM-DD):")
    tob = st.time_input("Enter your Time of Birth (HH:MM:SS in 24-hour format):")
    state = st.text_input("Enter your State:")
    city = st.text_input("Enter your City:")

    if st.button("Generate Kundali"):
        # Validate date-time input
        if not validate_datetime(dob.strftime("%Y-%m-%d"), tob.strftime("%H:%M:%S")):
            st.error("❌ Error: Invalid date or time format. Use YYYY-MM-DD for date and HH:MM:SS for time.")
            return

        lat, lon = get_lat_long(city, state)
        if lat is None:
            st.error("❌ Error: Unable to fetch latitude and longitude. Check city and state input.")
            return

        # Calculate Kundli data
        planet_positions = get_planet_positions(dob.strftime("%Y-%m-%d"), tob.strftime("%H:%M:%S"), lat, lon)
        ascendants = calculate_ascendants(dob.strftime("%Y-%m-%d"), tob.strftime("%H:%M:%S"), lat, lon)
        yogas = calculate_yogas(planet_positions)
        dasha = calculate_dasha()
        gemstones = suggest_gemstones(planet_positions)
        poojas = recommend_poojas(planet_positions)
        dos, donts = dos_and_donts(planet_positions)
        guidance = spiritual_guidance(planet_positions)

        # Prepare data for the chart
        house_labels = {i: str(i) for i in range(1, 13)}  # House numbers
        planets_in_houses = {planet: details["house"] for planet, details in planet_positions.items()}

        # Display Kundli Report
        st.subheader("Kundali Report")
        st.write(f"👤 **Name:** {name}")
        st.write(f"📅 **Date of Birth:** {dob.strftime('%Y-%m-%d')}")
        st.write(f"🕒 **Time of Birth:** {tob.strftime('%H:%M:%S')}")
        st.write(f"📍 **Birth Location:** {city}, {state} (Lat: {lat}, Lon: {lon})")


        st.write("\n🌟 All Ascendants (Lagna):")
        for house, asc in ascendants.items():
            st.write(f"House {house}: {asc}")

        st.write("\n🌌 Planetary Positions:")
        for planet, details in planet_positions.items():
            st.write(f"⭐ {planet}: House {details['house']}, Nakshatra: {details['nakshatra']}, Degrees: {details['degrees']}°")

        st.write("\n📖 Yogas Identified:")
        for yoga in yogas:
            st.write(f"- {yoga}")

        st.write("\n📅 Dasha Periods:")
        for period, planet in dasha.items():
            st.write(f"{period}: {planet}")

        st.write("\n💎 Suggested Gemstones:")
        for planet, gemstone in gemstones.items():
            st.write(f"{planet}: {gemstone}")

        st.write("\n🕉 Recommended Poojas:")
        for planet, pooja in poojas.items():
            st.write(f"{planet}: {pooja}")

        st.write("\n✅ Do's:")
        for do in dos:
            st.write(f"- {do}")

        st.write("\n❌ Don'ts:")
        for dont in donts:
            st.write(f"- {dont}")

        st.write("\n🌈 Spiritual Guidance:")
        for advice in guidance:
            st.write(f"- {advice}")

        # Plot the Kundli chart
        plot_kundli(house_labels, planets_in_houses, ascendants)

# Run the program
if __name__ == "__main__":
    main()