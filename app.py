import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Google Sheets imports
import gspread
from google.oauth2.service_account import Credentials

# ── Page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dlovan Delivery Logger",
    page_icon="🚚",
    layout="centered"
)

st.title("🚚 Dlovan Delivery Logger")
st.write("Fill in each delivery record, snap photos, and sync to Google Sheets.")

# ── Initialize DataFrame in session ─────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        columns=[
            "date","worker_name","driver_name",
            "track_plate","goods_description","goods_number","weight_tons",
            "plate_image_path","goods_image_path"
        ]
    )

# ── Setup Google Sheets client ───────────────────────────────────────
@st.experimental_singleton
def get_sheet():
    # load service account info from secrets
    info = st.secrets["gcp_service_account"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    client = gspread.authorize(creds)
    # open by URL and select first sheet
    SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1v5KVohFfBz98LrgApjDb-As06hUzgD_Dqxc7CoIOTrs/edit"
    sheet = client.open_by_url(SPREADSHEET_URL).sheet1
    return sheet

sheet = get_sheet()

# ── Data entry form ──────────────────────────────────────────────────
with st.form("entry_form", clear_on_submit=True):
    date = st.date_input("Date", datetime.today())
    worker_name = st.text_input("Worker Name")
    driver_name = st.text_input("Driver Name")
    track_plate = st.text_input("Track Plate Number")
    goods_description = st.text_input("Goods Description")
    goods_number = st.number_input("Number of Items", min_value=0, step=1)
    weight_tons = st.number_input("Weight (tons)", min_value=0.0, step=0.1, format="%.2f")
    plate_image = st.camera_input("📸 Capture Track Plate")
    goods_image = st.camera_input("📸 Capture Goods")

    submitted = st.form_submit_button("Submit Delivery")
    if submitted:
        date_str = date.strftime("%Y-%m-%d")
        # save images locally
        folder = os.path.join("data", f"{date_str}_{track_plate}")
        os.makedirs(folder, exist_ok=True)
        plate_path = os.path.join(folder, "plate.jpg")
        goods_path = os.path.join(folder, "goods.jpg")
        if plate_image: open(plate_path,"wb").write(plate_image.getvalue())
        if goods_image: open(goods_path,"wb").write(goods_image.getvalue())

        # build record
        new_row = {
            "date": date_str,
            "worker_name": worker_name,
            "driver_name": driver_name,
            "track_plate": track_plate,
            "goods_description": goods_description,
            "goods_number": goods_number,
            "weight_tons": weight_tons,
            "plate_image_path": plate_path,
            "goods_image_path": goods_path,
        }
        # append to session DataFrame
        new_df = pd.DataFrame([new_row])
        st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)

        # also append to Google Sheet
        # ensure header row exists
        if sheet.row_count == 0:
            sheet.append_row(list(st.session_state.df.columns), value_input_option="RAW")
        # append values
        sheet.append_row(list(new_row.values()), value_input_option="USER_ENTERED")

        st.success("✅ Delivery recorded locally & synced to Google Sheets!")

# ── Show table & download CSV ─────────────────────────────────────────
if not st.session_state.df.empty:
    st.subheader("All Deliveries (local)")
    st.dataframe(st.session_state.df)
    csv_bytes = st.session_state.df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download CSV",
        data=csv_bytes,
        file_name="dlovan_deliveries.csv",
        mime="text/csv",
    )
