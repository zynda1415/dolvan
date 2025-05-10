# … above unchanged …

    if submitted:
        # ensure storage folder
        date_str = date.strftime("%Y-%m-%d")
        folder = os.path.join("data", f"{date_str}_{track_plate}")
        os.makedirs(folder, exist_ok=True)

        # save images …
        # (same as before)

        # append record (fixed)
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
        new_df = pd.DataFrame([new_row])
        st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)

        st.success("✅ Delivery recorded!")

# … rest unchanged …
