import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dlovan Delivery Logger",
    page_icon="🚚",
    layout="centered"
)

st.title("🚚 Dlovan Delivery Logger")
st.write("Fill in each delivery record and snap photos. Then download your CSV.")

# ── load or initialize DataFrame ────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        columns=[
            "date",
            "worker_name",
            "driver_name",
            "track_plate",
            "goods_description",
            "goods_number",
            "weight_tons",
            "plate_image_path",
            "goods_image_path",
        ]
    )

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
        # ensure storage folder
        date_str = date.strftime("%Y-%m-%d")
        folder = os.path.join("data", f"{date_str}_{track_plate}")
        os.makedirs(folder, exist_ok=True)

        # save images to disk
        plate_path = os.path.join(folder, "plate.jpg")
        goods_path = os.path.join(folder, "goods.jpg")
        if plate_image:
            with open(plate_path, "wb") as f:
                f.write(plate_image.getvalue())
        if goods_image:
            with open(goods_path, "wb") as f:
                f.write(goods_image.getvalue())

        # append record
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
        st.session_state.df = st.session_state.df.append(new_row, ignore_index=True)
        st.success("✅ Delivery recorded!")

# ── show table & download ─────────────────────────────────────────────
if not st.session_state.df.empty:
    st.subheader("All Deliveries")
    st.dataframe(st.session_state.df)

    csv_bytes = st.session_state.df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download CSV",
        data=csv_bytes,
        file_name="dlovan_deliveries.csv",
        mime="text/csv",
    )
