import streamlit as st
import requests
import pandas as pd
import ast
from collections import defaultdict

API_url = "http://127.0.0.1:5000"



# ✅ MUST be first Streamlit command
st.set_page_config(page_title="My Flight App", page_icon="🛫", layout="wide")

# Then your usual app logic
st.title("Welcome to the Plane Dashboard")

if "page" not in st.session_state:
    st.session_state.page = "home"

#st.set_page_config(page_title="Plane Management System", layout="wide")
# Also will add flight destination for further use

# Add Plane Section
# Create 3 columns: content on the left, right and empty in the middle
left_col, _, right_col = st.columns([2, 1, 1])
with left_col:
    st.markdown("## ➕ Add a New Plane. ")
    ID = st.number_input("ID", min_value=1, step=1)
    name = st.text_input("Plane Name")
    model = st.text_input("Model")
    capacity = st.number_input("Capacity", min_value=1, step=1)
    from1 = st.text_input("Flight From")
    to1 = st.text_input("Flight destination")
    flight_date = st.text_input(
        "Flight Date (format: YYYY-MM-DD)",
        placeholder="e.g., 2025-05-10"
    )
    flight_status = st.text_input(
        "Flight Status",
        placeholder="e.g., Not Taken Off, Completed, Delayed"
    )
    submitted = st.button("Add Plane")

    if submitted:
        if not ID or not name or not model or not flight_date or not from1 or not to1 or not flight_status:
            st.error("Please fill in all fields and enter at least one flight date.")
        else:
            try:

                res = requests.post(f"{API_url}/add_plane", json={
                    "id": ID,
                    "name": name,
                    "model": model,
                    "capacity": int(capacity),
                    "date": flight_date,
                    "from": from1,
                    "to": to1,
                    "status": flight_status,
                })
                if res.status_code == 201:
                    st.success(f"✅ Plane '{name}' added successfully!")
                else:
                    st.error(f"❌ Error: {res.json().get('error', 'Unknown error')}")
            except Exception as e:
                st.error("⚠️ Could not connect to the backend.")
                st.exception(e)


with right_col:
    st.markdown("## ➕ Add a New Flight")
    ID = st.number_input("ID", min_value=1, step=1, key="ID")
    from1 = st.text_input("Flight From", key="from_location")
    to1 = st.text_input("Flight Destination", key="to_location")
    add_date = st.text_input("Flight Date (format: YYYY-MM-DD)", 
        placeholder="e.g., 2025-06-10",
        key="add_date"
    )
    flight_status = st.text_input(
        "Flight Status",
        placeholder="e.g., Not Taken Off, Completed, Delayed",
        key="flight_status"
    )


    if st.button("Add Flight"):
        add_date_clean = add_date.strip()

        if ',' in add_date_clean:
            st.warning("❗ Please enter only one date.")
        elif add_date_clean == "":
            st.warning("❗ Please enter a valid date.")
        elif from1 == "" or to1 == "":
            st.warning("❗ Please enter valid departure and destination locations.")
        else:
            response = requests.post(f"{API_url}/add_flight/{ID}/{add_date_clean}/{from1}/{to1}/{flight_status}")
            if response.status_code == 200:
                st.success("✅ New Flight added successfully!")
            elif response.status_code == 400:
                st.error("❌ Flight date already exists!")
            else:
                st.error("❌ Failed to add flight. Please check the ID.")



# Delete Plane Section
# Create 3 columns: content on the left, right and empty in the middle
left_col, _, right_col = st.columns([1, 1, 1])

with left_col:
    st.markdown("## 🗑️ Delete Plane")
    delete_id1 = st.number_input("Enter Plane ID to delete", min_value=0, step=1, key="delete_id1")
    if st.button("Delete Plane"):
        response1 = requests.delete(f"{API_url}/delete_plane/{delete_id1}")
        if response1.status_code == 200:
            st.success("✅ Plane deleted successfully!")
        else:
            st.error("❌ Failed to delete plane. Please check the ID.")


with right_col:
    st.markdown("## 🗑️ Delete Flight")
    id1 = st.number_input("Enter Plane ID to delete the flight", min_value=0, step=1, key="id1")
    delete_date = st.text_input("Enter the date of flight to cancel", 
        placeholder="e.g., 2025-05-10")
    
    if st.button("Delete Flight"):
        # Strip whitespace and validate single date
        delete_date_clean = delete_date.strip()

        if ',' in delete_date_clean:
            st.warning("❗ Please enter only one date at a time.")
        elif delete_date_clean == "":
            st.warning("❗ Please enter a valid date.")
        else:
            response2 = requests.post(f"{API_url}/delete_flight/{id1}/{delete_date_clean}")
            if response2.status_code == 200:
                st.success("✅ Flight cancelled successfully!")
            else:
                st.error("❌ Failed to delete flight. Please check the ID and the date.")



# View Planes Section
st.header("📋 View All Planes")
try:
    res = requests.get(f"{API_url}/planes")
    flights = res.json()

    if not flights:
        st.info("No flights found.")
    else:
        df = pd.DataFrame(flights)

        # Group flights into planes with routes
        planes_dict = defaultdict(lambda: {
            "id": None, "name": "", "model": "", "capacity": 0, "routes": []
        })

        for _, row in df.iterrows():
            key = (row['id'], row['name'], row['model'], row['capacity'])
            plane_entry = planes_dict[key]
            plane_entry['id'] = row['id']
            plane_entry['name'] = row['name']
            plane_entry['model'] = row['model']
            plane_entry['capacity'] = row['capacity']
            plane_entry['routes'].append({
                'date': row['date'],
                'from': row['from'],
                'to': row['to'],
                'status': row['status']
            })

        # Convert to list of grouped planes
        grouped_planes = list(planes_dict.values())

        # Display in 4 cards per row
        for i in range(0, len(grouped_planes), 4):
            cols = st.columns(4)
            for j in range(4):
                if i + j < len(grouped_planes):
                    plane = grouped_planes[i + j]
                    with cols[j]:
                        with st.expander(f"{plane['name']} - {plane['model']}"):
                            st.markdown(f"""
                            **✈️ Plane ID**: `{plane['id']}`  
                            **🧾 Name**: {plane['name']}  
                            **🛠️ Model**: {plane['model']}  
                            **👥 Capacity**: {plane['capacity']}  
                            """)
                            st.markdown("**📍 Routes:**")
                            for route in plane['routes']:
                                st.markdown(f"- **{route['from']} → {route['to']}** on `{route['date']}` – Status: *{route['status']}*")

        # Optionally download grouped data as flat CSV
        csv = df.to_csv(index=False)
        st.download_button("📥 Download Flights as CSV", csv, "flights.csv", "text/csv")

except Exception as e:
    st.error("🚫 Could not connect to Flask API.")
    st.exception(e)



#Chat model section
st.header("Ask assistant")
if st.session_state.page == "home":

    if st.button("💬 Open Chat"):
        st.session_state.page = "chat"


elif st.session_state.page == "chat":
    from chat_page import show_chat
    show_chat()
     
