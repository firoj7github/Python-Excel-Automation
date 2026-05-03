import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import time

st.set_page_config(page_title="Universal Data Formatter", layout="centered")

st.title("📊 Excel & CSV Data Formatter")
st.write("Please upload your **Input Data** and the **Target Format Sheet**.")

# 1. File Upload Options
data_file = st.file_uploader("Upload Input Data (Excel or CSV)", type=["xlsx", "csv"])
format_file = st.file_uploader("Upload Target Format (Excel or CSV)", type=["xlsx", "csv"])

def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

if data_file and format_file:
    try:
        df_data = load_data(data_file)
        df_format = load_data(format_file)
        target_columns = df_format.columns.tolist()
        
        st.success("Files uploaded successfully!")

        # --- Date & Fixed Time Settings ---
        st.markdown("---")
        st.subheader("📅 Date & Custom Time Settings")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            gen_date_format = st.text_input("General Date Format", value="%Y-%m-%d")
            st.caption("For: connection_date, DOB")
        
        with col2:
            # এখানে ইউজার ম্যানুয়ালি সময় সিলেক্ট করতে পারবে
            fixed_time = st.time_input("Set Expiration Time", time(23, 59)) 
            st.caption("Default: 11:59 PM")

        with col3:
            exp_date_format = st.text_input("Expire Date Format", value="%Y-%m-%d %H:%M:%S")
            st.caption("Final output style")

        # Transformation Logic
        final_df = pd.DataFrame()
        for col in target_columns:
            if col in df_data.columns:
                if col in ['connection_date', 'date_of_birth']:
                    final_df[col] = pd.to_datetime(df_data[col], errors='coerce').dt.strftime(gen_date_format)
                
                elif col == 'expire_date':
                    # ১. প্রথমে ডাটাবেজের তারিখকে ডেট-টাইম ফরম্যাটে নিচ্ছি
                    temp_dt = pd.to_datetime(df_data[col], errors='coerce')
                    # ২. তারিখের সাথে ইউজারের সিলেক্ট করা সময় (fixed_time) যোগ করছি
                    final_df[col] = temp_dt.apply(
                        lambda d: d.replace(hour=fixed_time.hour, minute=fixed_time.minute, second=fixed_time.second) 
                        if pd.notnull(d) else ""
                    )
                    # ৩. এবার কাঙ্ক্ষিত ফরম্যাটে সাজাচ্ছি
                    final_df[col] = pd.to_datetime(final_df[col]).dt.strftime(exp_date_format)
                
                else:
                    final_df[col] = df_data[col]
            else:
                final_df[col] = ""

        st.write("### Preview of Processed Data:")
        st.dataframe(final_df.head())

        # --- Output Format Selection ---
        st.markdown("---")
        output_format = st.radio("Choose output format:", ("Excel (.xlsx)", "CSV (.csv)"))

        output = BytesIO()
        if output_format == "Excel (.xlsx)":
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False)
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_ext = "xlsx"
        else:
            csv_data = final_df.to_csv(index=False).encode('utf-8')
            output.write(csv_data)
            mime_type = "text/csv"
            file_ext = "csv"

        st.download_button(
            label=f"📥 Download Formatted {file_ext.upper()}",
            data=output.getvalue(),
            file_name=f"final_report.{file_ext}",
            mime=mime_type
        )

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Waiting for files...")