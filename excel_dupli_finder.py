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

    st.write("Selected columns:", columns)

    if st.button("Find Duplicates"):
        if columns:
            duplicates = df[df.duplicated(subset=columns, keep=False)]
            st.write("Duplicates found:", duplicates)
            st.dataframe(duplicates)

            # Download button for duplicates
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                duplicates.to_excel(writer, index=False, sheet_name='Duplicates')
            buffer.seek(0)
            st.download_button(
                label="Download Duplicates",
                data=buffer,
                file_name="duplicates.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Please select at least one column to check for duplicates.")
   