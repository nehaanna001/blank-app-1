import streamlit as st
import requests
from streamlit_folium import folium_static
import folium

# Replace with your AirVisual API key
api_key = "your_api_key_here"

st.title("Weather and Air Quality Web App")
st.header("Streamlit and AirVisual API")

category = st.selectbox("Select location by:", ["By City, State, and Country", "By Nearest City (IP Address)", "By Latitude and Longitude"])

# Function to fetch list of countries from AirVisual API
@st.cache
def generate_list_of_countries():
    countries_url = f"https://api.airvisual.com/v2/countries?key={api_key}"
    countries_dict = requests.get(countries_url).json()
    return countries_dict

# Function to fetch list of states from AirVisual API based on selected country
@st.cache
def generate_list_of_states(country_selected):
    states_url = f"https://api.airvisual.com/v2/states?country={country_selected}&key={api_key}"
    states_dict = requests.get(states_url).json()
    return states_dict

# Function to fetch list of cities from AirVisual API based on selected state and country
@st.cache
def generate_list_of_cities(state_selected, country_selected):
    cities_url = f"https://api.airvisual.com/v2/cities?state={state_selected}&country={country_selected}&key={api_key}"
    cities_dict = requests.get(cities_url).json()
    return cities_dict

# Function to display weather and air quality information
def display_data(data):
    city = data["data"]["city"]
    state = data["data"]["state"]
    country = data["data"]["country"]
    temperature = data["data"]["current"]["weather"]["tp"]
    humidity = data["data"]["current"]["weather"]["hu"]
    aqi = data["data"]["current"]["pollution"]["aqius"]

    st.subheader(f"Weather and Air Quality in {city}, {state}, {country}")
    st.write(f"Temperature: {temperature} °C")
    st.write(f"Humidity: {humidity}%")
    st.write(f"Air Quality Index (AQI): {aqi}")

    latitude = data["data"]["location"]["coordinates"]["latitude"]
    longitude = data["data"]["location"]["coordinates"]["longitude"]
    map_creator(latitude, longitude)

# Function to create Folium map
@st.cache
def map_creator(latitude, longitude):
    m = folium.Map(location=[latitude, longitude], zoom_start=10)
    folium.Marker([latitude, longitude], popup="Location").add_to(m)
    folium_static(m)

# Main logic based on user selection
if category == "By City, State, and Country":
    countries_dict = generate_list_of_countries()

    if countries_dict["status"] == "success":
        countries_list = [country["country"] for country in countries_dict["data"]]
        country_selected = st.selectbox("Select a country", [""] + countries_list)

        if country_selected:
            states_dict = generate_list_of_states(country_selected)

            if states_dict["status"] == "success":
                states_list = [state["state"] for state in states_dict["data"]]
                state_selected = st.selectbox("Select a state", [""] + states_list)

                if state_selected:
                    cities_dict = generate_list_of_cities(state_selected, country_selected)

                    if cities_dict["status"] == "success":
                        cities_list = [city["city"] for city in cities_dict["data"]]
                        city_selected = st.selectbox("Select a city", [""] + cities_list)

                        if city_selected:
                            aqi_data_url = f"https://api.airvisual.com/v2/city?city={city_selected}&state={state_selected}&country={country_selected}&key={api_key}"
                            aqi_data_dict = requests.get(aqi_data_url).json()

                            if aqi_data_dict["status"] == "success":
                                display_data(aqi_data_dict)
                            else:
                                st.warning("No data available for this location.")
                    else:
                        st.warning("No cities available for this state and country.")
            else:
                st.warning("No states available for this country.")
    else:
        st.error("Failed to retrieve countries. Please try again later.")

elif category == "By Nearest City (IP Address)":
    url = f"https://api.airvisual.com/v2/nearest_city?key={api_key}"
    aqi_data_dict = requests.get(url).json()

    if aqi_data_dict["status"] == "success":
        display_data(aqi_data_dict)
    else:
        st.warning("No data available for your current location.")

elif category == "By Latitude and Longitude":
    latitude = st.text_input("Enter latitude:")
    longitude = st.text_input("Enter longitude:")

    if st.button("Submit"):
        if latitude and longitude:
            url = f"https://api.airvisual.com/v2/nearest_city?lat={latitude}&lon={longitude}&key={api_key}"
            aqi_data_dict = requests.get(url).json()

            if aqi_data_dict["status"] == "success":
                display_data(aqi_data_dict)
            else:
                st.warning("No data available for this location.")
        else:
            st.warning("Please enter both latitude and longitude.")
