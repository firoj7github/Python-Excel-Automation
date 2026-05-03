import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Excel Formatter", layout="centered")

st.title("📊 Excel Data Formatter")
st.write("Aponar Data Sheet ebong Target Format Sheet upload korun.")

# 1. File Upload Options
data_file = st.file_uploader("Upload Input Data (Excel)", type=["xlsx"])
format_file = st.file_uploader("Upload Target Format (Excel)", type=["xlsx"])

if data_file and format_file:
    try:
        # Data Load kora
        df_data = pd.read_excel(data_file)
        df_format = pd.read_excel(format_file)
        
        target_columns = df_format.columns.tolist()
        
        st.success("Files uploaded successfully!")
        
        # Transformation Logic
        final_df = pd.DataFrame()
        for col in target_columns:
            if col in df_data.columns:
                final_df[col] = df_data[col]
            else:
                final_df[col] = ""  # Column na thakle blank
        
        st.write("### Preview of Processed Data:")
        st.dataframe(final_df.head())

        # Download Option
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Download Formatted Excel",
            data=output.getvalue(),
            file_name="final_formatted_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Opekkhay achhi... Doya kore duto file-ই upload korun.")