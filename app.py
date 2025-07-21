"""
Healthcare Operations Dashboard
Created by: Beyonka Powell

Description:
This Streamlit app visualizes healthcare operations data using a SQLite database.
It covers claims, lab turnaround performance, appointment behavior, and staffing workload.
Built with Python, SQL, Pandas, and Streamlit’s native charting features.
"""

import streamlit as st
import sqlite3
import pandas as pd

# --- Setup Page ---
st.set_page_config(page_title="Healthcare Dashboard", layout="wide")
st.title("🏥 Healthcare Operations Dashboard")
st.markdown("Use this dashboard to monitor lab performance, claims processing, patient behavior, and staff trends.")

# --- Connect to SQLite database ---
conn = sqlite3.connect("healthcare_data.db")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")
lab_dept = st.sidebar.selectbox("Select Lab Department", ["All", "Hematology", "Microbiology", "Chemistry"])

# =========================
# 📄 CLAIMS SECTION
# =========================
st.subheader("📄 Claims Summary")
claims = pd.read_sql("SELECT Status, COUNT(*) as Total FROM claims GROUP BY Status", conn)
st.bar_chart(claims.set_index("Status"))

# =========================
# 🧪 LAB RESULTS SECTION
# =========================
st.subheader("🧪 Lab SLA Performance")

lab_query = "SELECT * FROM lab_results"
if lab_dept != "All":
    lab_query += f" WHERE Department = '{lab_dept}'"
lab = pd.read_sql(lab_query, conn)

sla_summary = lab.groupby("SLA_Violation").size().reset_index(name="Total")
st.dataframe(sla_summary, use_container_width=True)

avg_tat = lab.groupby("Department")["TAT_Hours"].mean().round(2).reset_index()
st.markdown("**Average TAT by Department**")
st.bar_chart(avg_tat.set_index("Department"))

# =========================
# 📅 APPOINTMENTS SECTION
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Appointment Status")
    appt_status = pd.read_sql("SELECT Status, COUNT(*) as Total FROM appointments GROUP BY Status", conn)
    st.bar_chart(appt_status.set_index("Status"))

with col2:
    st.subheader("👤 No-Shows by Age Group")
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
    st.dataframe(no_show_by_age, use_container_width=True)

# =========================
# 👥 STAFFING SECTION
# =========================
st.subheader("👥 Staffing Summary")

staff_hours = pd.read_sql("SELECT Role, SUM(Hours_Worked) AS Total_Hours FROM staffing GROUP BY Role", conn)
st.bar_chart(staff_hours.set_index("Role"))

shift_count = pd.read_sql("""
    SELECT Department, Shift, COUNT(*) AS Shift_Count
    FROM staffing
    GROUP BY Department, Shift
""", conn)
st.dataframe(shift_count, use_container_width=True)

# --- Close connection ---
conn.close()
