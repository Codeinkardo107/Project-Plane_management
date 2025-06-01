import streamlit as st
import requests
import pandas as pd

API_url = "http://127.0.0.1:5000"

st.set_page_config(page_title="Plane Management System", layout="wide")
st.title("✈️ Plane Management")


# Add Plane Section
# Create 3 columns: content on the left, right and empty in the middle
left_col, _, right_col = st.columns([2, 1, 1])
with left_col:
    st.markdown("## ➕ Add a New Plane")
    ID = st.number_input("ID", min_value=1, step=1)
    name = st.text_input("Plane Name")
    model = st.text_input("Model")
    capacity = st.number_input("Capacity", min_value=1, step=1)
    flight_dates_input = st.text_area(
        "Flight Dates (comma-separated, format: YYYY-MM-DD)",
        placeholder="e.g., 2025-06-01, 2025-05-10"
    )
    submitted = st.button("Add Plane")

    if submitted:
        flight_dates = [d.strip() for d in flight_dates_input.split(",") if d.strip()]
        if not ID or not name or not model or not flight_dates:
            st.error("Please fill in all fields and enter at least one flight date.")
        else:
            try:
                res = requests.post(f"{API_url}/add_plane", json={
                    "id": ID,
                    "name": name,
                    "model": model,
                    "capacity": int(capacity),
                    "flight_dates": flight_dates
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
    add_date = st.text_input( "Flight Date to add (format: YYYY-MM-DD)",
        placeholder="e.g., 2025-06-01, 2025-05-10"
    )

    if st.button("Add Flight"):
        add_date_clean = add_date.strip()

        if ',' in add_date_clean:
            st.warning("❗ Please enter only one date.")
        elif add_date_clean == "":
            st.warning("❗ Please enter a valid date.")
        else:
            response = requests.post(f"{API_url}/add_flight/{ID}/{add_date_clean}")
            if response.status_code == 200:
                st.success("✅ Flight date added successfully!")
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
        placeholder="e.g., 2025-06-01, 2025-05-10")
    
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
    planes = res.json()

    if not planes:
        st.info("No planes found.")
    else:
        df = pd.DataFrame(planes)
        df['flight_dates'] = df['flight_dates'].apply(lambda d: ", ".join(d) if isinstance(d, list) else str(d))


        display_df = df[['id', 'name', 'model', 'capacity', 'flight_dates']]
        st.dataframe(display_df)

        # CSV export
        csv = df.to_csv(index=False)
        st.download_button("📥 Download as CSV", csv, "planes.csv", "text/csv")
except Exception as e:
    st.error("🚫 Could not connect to Flask API.")
    st.exception(e)
