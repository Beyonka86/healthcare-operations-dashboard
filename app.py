"""
Healthcare Operations Dashboard (Interactive)
Created by: Beyonka Powell

Description:
An interactive dashboard for monitoring claims, lab turnaround, patient no-shows,
and staffing trends using Python, SQLite, Pandas, and Streamlit.
Includes sidebar filters, date ranges, and toggle views.
"""

import streamlit as st
import sqlite3
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="Healthcare Dashboard", layout="wide")
st.title("🏥 Healthcare Operations Dashboard")

st.markdown("Use the sidebar to filter and explore healthcare operations data from lab, appointments, claims, and staffing.")

# --- Connect to DB ---
conn = sqlite3.connect("healthcare_data.db")

# =====================
# SIDEBAR FILTERS
# =====================
st.sidebar.header("🔍 Filters")

# Lab filters
lab_dept = st.sidebar.selectbox("Lab Department", ["All", "Hematology", "Microbiology", "Chemistry"])
test_filter_query = "SELECT DISTINCT Test_Name FROM lab_results"
all_tests = pd.read_sql(test_filter_query, conn)["Test_Name"].tolist()
selected_tests = st.sidebar.multiselect("Lab Test Types", all_tests, default=all_tests)

# Appointment date range
st.sidebar.markdown("---")
date_range = st.sidebar.date_input("Appointment Date Range", [pd.to_datetime("2025-06-01"), pd.to_datetime("2025-06-30")])

# Toggle view option
view_mode = st.sidebar.radio("View Mode", ["📊 Charts", "📋 Tables"])

# Refresh button
if st.sidebar.button("🔄 Refresh Dashboard"):
    st.experimental_rerun()

# =====================
# CLAIMS SECTION
# =====================
st.subheader("📄 Claims Overview")
claims = pd.read_sql("SELECT Status, COUNT(*) as Total FROM claims GROUP BY Status", conn)

if view_mode == "📊 Charts":
    st.bar_chart(claims.set_index("Status"))
else:
    st.dataframe(claims)

# =====================
# LAB RESULTS SECTION
# =====================
st.subheader("🧪 Lab SLA Performance")

lab_query = "SELECT * FROM lab_results"
if lab_dept != "All":
    lab_query += f" WHERE Department = '{lab_dept}'"
lab = pd.read_sql(lab_query, conn)
lab = lab[lab["Test_Name"].isin(selected_tests)]

sla_summary = lab.groupby("SLA_Violation").size().reset_index(name="Total")
st.markdown("**SLA Violation Summary**")
st.dataframe(sla_summary)

avg_tat = lab.groupby("Department")["TAT_Hours"].mean().round(2).reset_index()
st.markdown("**Average Turnaround Time by Department**")
if view_mode == "📊 Charts":
    st.bar_chart(avg_tat.set_index("Department"))
else:
    st.dataframe(avg_tat)

# =====================
# APPOINTMENTS SECTION
# =====================
st.subheader("📅 Appointment Trends")

start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1])
appt_query = f"""
    SELECT * FROM appointments
    WHERE DATE(Appointment_Time) BETWEEN '{start_date}' AND '{end_date}'
"""
appointments = pd.read_sql(appt_query, conn)

col1, col2 = st.columns(2)

with col1:
    appt_status = appointments.groupby("Status").size().reset_index(name="Total")
    st.markdown("**Status Summary**")
    if view_mode == "📊 Charts":
        st.bar_chart(appt_status.set_index("Status"))
    else:
        st.dataframe(appt_status)

with col2:
    no_show_by_age = pd.read_sql("""
        SELECT 
          CASE 
            WHEN Age < 30 THEN 'Under 30'
            WHEN Age BETWEEN 30 AND 49 THEN '30-49'
            WHEN Age BETWEEN 50 AND 69 THEN '50-69'
            ELSE '70+'
          END AS Age_Group,
          COUNT(*) AS Total_Appointments,
          SUM(CASE WHEN Status = 'No-Show' THEN 1 ELSE 0 END) AS No_Shows
        FROM appointments
        GROUP BY Age_Group
    """, conn)
    st.markdown("**No-Shows by Age Group**")
    st.dataframe(no_show_by_age)

# =====================
# STAFFING SECTION
# =====================
st.subheader("👥 Staffing Summary")

staff_hours = pd.read_sql("SELECT Role, SUM(Hours_Worked) AS Total_Hours FROM staffing GROUP BY Role", conn)
st.markdown("**Hours Worked by Role**")
if view_mode == "📊 Charts":
    st.bar_chart(staff_hours.set_index("Role"))
else:
    st.dataframe(staff_hours)

shift_count = pd.read_sql("""
    SELECT Department, Shift, COUNT(*) AS Shift_Count
    FROM staffing
    GROUP BY Department, Shift
""", conn)
st.markdown("**Shift Count by Department**")
st.dataframe(shift_count)

# --- Close connection ---
conn.close()

