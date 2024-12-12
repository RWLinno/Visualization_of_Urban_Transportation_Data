import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import random

# Load parking lot data from CSV file
@st.cache_data
def load_parking_data(file_path):
    data = pd.read_csv(file_path)
    # Keep only necessary columns
    return data[["LotID", "Latitude", "Longitude"]].dropna()

# Generate random parking volume data
def generate_parking_volume():
    return [random.randint(50, 200) for _ in range(30)] + [random.randint(60, 150) for _ in range(7)]

# Generate random vehicle data
def generate_vehicle_data():
    car_types = ["Sedan", "SUV", "Pickup", "Truck"]
    return {car_type: {"Fuel": random.randint(50, 200), "Electric": random.randint(20, 80)} for car_type in car_types}

# Initialize Streamlit
st.set_page_config(layout="wide")
st.title("Singapore Parking Lots Interactive Dashboard")

# Load parking lot data
parking_data_file = "lots_1687.csv"
parking_data = load_parking_data(parking_data_file)

# Manage selected parking lot using session_state
if "selected_parking_lot" not in st.session_state:
    st.session_state["selected_parking_lot"] = None

# Layout: Left map, Right two charts
col1, col2 = st.columns([1, 2])

# Left map
with col1:
    st.subheader("Singapore Parking Lots Map")

    # Initialize map
    m = folium.Map(location=[1.35, 103.85], zoom_start=15)
    for _, lot in parking_data.iterrows():
        icon_color = "red" if lot["LotID"] == st.session_state["selected_parking_lot"] else "blue"
        folium.Marker(
            location=[lot["Latitude"], lot["Longitude"]],
            popup=lot["LotID"],
            tooltip=lot["LotID"],
            icon=folium.Icon(color=icon_color)
        ).add_to(m)

    # Display map and capture interactions
    map_data = st_folium(m, width=600, height=600)

    # Check for selected parking lot
    if map_data and "last_object_clicked" in map_data and map_data["last_object_clicked"]:
        for _, lot in parking_data.iterrows():
            if (
                lot["Latitude"] == map_data["last_object_clicked"]["lat"]
                and lot["Longitude"] == map_data["last_object_clicked"]["lng"]
            ):
                st.session_state["selected_parking_lot"] = lot["LotID"]
                break

# Right charts
with col2:
    if st.session_state["selected_parking_lot"] is not None:
        selected_lot = parking_data.loc[
            parking_data["LotID"] == st.session_state["selected_parking_lot"]
        ].iloc[0]

        st.write(f"**Parking Lot**: {selected_lot['LotID']}")
        st.write(f"**Coordinates**: {selected_lot['Latitude']:.6f}, {selected_lot['Longitude']:.6f}")

        # Line chart for parking volume
        parking_volume = generate_parking_volume()
        dates = pd.date_range(start="2024-01-01", periods=30).tolist() + pd.date_range(start="2024-02-01", periods=7).tolist()
        df_parking_volume = pd.DataFrame({
            "Date": dates,
            "Parking Volume": parking_volume,
            "Type": ["Historical Data"] * 30 + ["Forecast Data"] * 7
        })

        # Stacked bar chart for vehicle types
        vehicle_data = generate_vehicle_data()
        car_types = list(vehicle_data.keys())
        fuel_cars = [vehicle_data[car]["Fuel"] for car in car_types]
        electric_cars = [vehicle_data[car]["Electric"] for car in car_types]

        # Horizontal layout for charts
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.subheader("Parking Volume Over Time")
            fig_line = px.line(df_parking_volume, x="Date", y="Parking Volume", color="Type", markers=True,
                               title="Monthly Parking Volume and Weekly Forecast")
            st.plotly_chart(fig_line, use_container_width=True)

        with fig_col2:
            st.subheader("Vehicle Type Distribution")
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name="Fuel", x=car_types, y=fuel_cars, marker_color="blue"))
            fig_bar.add_trace(go.Bar(name="Electric", x=car_types, y=electric_cars, marker_color="green"))
            fig_bar.update_layout(
                barmode="stack",
                title="Electric vs Fuel Vehicles by Type",
                xaxis_title="Vehicle Type",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("Please select a parking lot to view details.")