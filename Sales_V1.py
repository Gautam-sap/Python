import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Sales Ranking App", layout="wide")

st.title("📊 Sales Ranking Dashboard")
st.write(
    "Change **Units** or **Unit_price** below. The app will automatically recalculate **Sale_amt** and update the **Rank**."
)

uploaded_file = st.file_uploader(
    "Choose an Excel file", type=["xlsx", "xls", "xlsm"]
)

if uploaded_file is not None:
    try:
        # Load data once and cache it in the session state to prevent losing edits
        if "df" not in st.session_state:
            initial_df = pd.read_excel(uploaded_file)
            initial_df.columns = initial_df.columns.str.strip()
            st.session_state.df = initial_df

        df = st.session_state.df

        # Validate that the required columns exist
        required_cols = ["Units", "Unit_price"]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(
                f"❌ Error: Missing required columns: {', '.join(missing_cols)}"
            )
            st.write("**Available columns found:**", list(df.columns))
        else:
            # 1. Automatically Recalculate Sale_amt based on the formula
            df["Sale_amt"] = df["Units"] * df["Unit_price"]

            # 2. Recalculate Rank based on the new Sale_amt
            df["Rank"] = df["Sale_amt"].rank(ascending=False, method="min")

            # Organize columns: Place Rank and calculation metrics at the front
            front_cols = ["Rank", "Units", "Unit_price", "Sale_amt"]
            other_cols = [col for col in df.columns if col not in front_cols]
            df = df[front_cols + other_cols]

            # Sort dataset by rank so the highest sales stay on top
            df = df.sort_values(by="Rank").reset_index(drop=True)

            st.subheader(
                "📝 Edit Data Below (Double-click Units or Unit_price to edit)"
            )

            # 3. Interactive Editor (Lock Rank and Sale_amt since they auto-calculate)
            edited_df = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                disabled=["Rank", "Sale_amt"],
            )

            # Update the session state with modifications
            st.session_state.df = edited_df

            # 4. Save and Export
            st.markdown("---")
            st.subheader("💾 Export Changes")

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                edited_df.to_excel(
                    writer, index=False, sheet_name="Recalculated Sales"
                )
            download_data = buffer.getvalue()

            st.download_button(
                label="📥 Download Updated Excel File",
                data=download_data,
                file_name="recalculated_ranked_sales.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    if "df" in st.session_state:
        del st.session_state.df
    st.info("💡 Please upload an Excel file to get started.")
