# Required packages
import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Excel Duplicate Finder")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Preview of data:", df.head())

    columns = st.multiselect("Select columns to check for duplicates", df.columns.tolist())

    if st.button("Find Duplicates"):
        if columns:
            df["Is_Duplicate"] = df.duplicated(subset=columns, keep=False)
            st.write(df)

            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label="Download Updated Excel",
                data=buffer,
                file_name="duplicates_checked.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Please select at least one column.")
