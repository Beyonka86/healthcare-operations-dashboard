import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect(r"C:\Users\Beyonka\HealthcareProject\CSV\healthcare_data.db")
# Query 1: Preview the claims table
query = "SELECT * FROM claims LIMIT 5"
claims_preview = pd.read_sql(query, conn)
print("Preview of Claims Table:")
print(claims_preview)

# Query 2: Count of claims by status
status_query = """
SELECT Status, COUNT(*) AS Total
FROM claims
GROUP BY Status
"""
status_summary = pd.read_sql(status_query, conn)
print("Claims by Status:")
print(status_summary)


# Query 3: Count SLA Violations in Lab Results
sla_query = """
SELECT SLA_Violation, COUNT(*) AS Total
FROM lab_results
GROUP BY SLA_Violation
"""
sla_summary = pd.read_sql(sla_query, conn)
print("Lab SLA Violations:")
print(sla_summary)

# Query 4: Avg TAT by Department
tat_query = """
SELECT Department, ROUND(AVG(TAT_Hours), 2) AS Avg_TAT
FROM lab_results
GROUP BY Department
"""
tat_summary = pd.read_sql(tat_query, conn)
print("Average Turnaround Time by Department:")
print(tat_summary)

# Query 7: Total Hours Worked by Role
role_query = """
SELECT Role, SUM(Hours_Worked) AS Total_Hours
FROM staffing
GROUP BY Role
"""
role_summary = pd.read_sql(role_query, conn)
print("Total Hours Worked by Role:")
print(role_summary)

# Query 8: Shift Count by Department
shift_query = """
SELECT Department, Shift, COUNT(*) AS Shift_Count
FROM staffing
GROUP BY Department, Shift
ORDER BY Department, Shift
"""
shift_summary = pd.read_sql(shift_query, conn)
print("Shift Distribution by Department:")
print(shift_summary)

# Close the connection
conn.close()