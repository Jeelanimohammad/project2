"""
app.py
------
Main Streamlit Application for Employee Management & Attendance System.
Entry point containing:
- Sidebar Navigation
- Modern Dashboard with KPIs (Total Employees, Present Today, Absent Today, Average Attendance)
- Routing to Employee Management, Attendance Management, Search, and Reports
"""

import streamlit as st
import pandas as pd
from datetime import date
import database as db
import employee
import attendance

# -------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# -------------------------------------------------------------
st.set_page_config(
    page_title="Employee Management & Attendance System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished, clean, professional presentation
st.markdown("""
<style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1rem 1.25rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #475569;
        font-size: 0.875rem;
    }
    div[data-testid="stMetricValue"] {
        color: #0f172a;
        font-weight: 700;
        font-size: 1.85rem;
    }
    
    /* Header Styling */
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.25rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f1f5f9;
        border-right: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


def init_app():
    """Ensure database tables exist on startup and seed data if empty."""
    db.create_tables()
    # Check if empty; if so, automatically seed sample data for immediate readiness
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM employees;")
    count = c.fetchone()[0]
    conn.close()

    if count == 0:
        db.seed_sample_data()


# Initialize database
init_app()


# -------------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏢 HR Portal")
    st.markdown("**Employee & Attendance System**")
    st.caption("Cloud Data Engineering Portfolio Project")
    st.markdown("---")

    menu_option = st.radio(
        "Navigation Menu",
        [
            "📊 Dashboard",
            "👥 Employee Management",
            "📅 Attendance Management",
            "🔍 Employee Search",
            "📈 Attendance Report"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("### ⚙️ Database Status")
    st.markdown("• **Engine:** SQLite 3")
    st.markdown("• **Mode:** Local Relational DB")

    # Quick seed / reload button
    if st.button("🔄 Reload Sample Data", use_container_width=True):
        db.seed_sample_data()
        st.success("Sample data loaded!")
        st.rerun()

    st.markdown("---")
    st.caption("Built with Python, Streamlit, SQLite & Pandas")


# -------------------------------------------------------------
# DASHBOARD VIEW
# -------------------------------------------------------------
def render_dashboard():
    st.markdown('<div class="main-title">📊 Executive Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Real-time overview of workforce metrics, daily attendance, and team distribution.</div>', unsafe_allow_html=True)

    # Date selector for snapshot
    col_d, _ = st.columns([2, 4])
    with col_d:
        selected_date = st.date_input("Attendance Snapshot Date:", value=date.today(), key="dash_date")

    # Retrieve metrics from database
    metrics = db.get_dashboard_metrics(target_date=selected_date)

    # 4 Main KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total Employees",
            value=metrics["total_employees"],
            help="Total number of active registered employees"
        )
    with col2:
        st.metric(
            label="Present Today",
            value=metrics["present_today"],
            help=f"Employees marked Present on {selected_date}"
        )
    with col3:
        st.metric(
            label="Absent Today",
            value=metrics["absent_today"],
            help=f"Employees marked Absent on {selected_date}"
        )
    with col4:
        st.metric(
            label="Average Attendance",
            value=f"{metrics['average_attendance']}%",
            help="Overall historical attendance rate across organization"
        )

    st.markdown("---")

    # Department Breakdown & Recent Activity
    c_left, c_right = st.columns([1.5, 1])

    with c_left:
        st.markdown("#### 🏢 Employees by Department")
        employees_df = db.get_employees()
        if not employees_df.empty:
            dept_counts = employees_df['department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Count']
            st.bar_chart(data=dept_counts.set_index('Department'))
        else:
            st.info("No employee records to visualize.")

    with c_right:
        st.markdown(f"#### 📋 Attendance for {selected_date}")
        today_att = db.get_attendance(start_date=selected_date, end_date=selected_date)
        if not today_att.empty:
            st.dataframe(
                today_att[['employee_id', 'name', 'department', 'status']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "employee_id": "ID",
                    "name": "Name",
                    "department": "Dept",
                    "status": "Status"
                }
            )
        else:
            st.info(f"No attendance recorded yet for {selected_date}.")
            st.caption("Go to 'Attendance Management' to log attendance.")

    st.markdown("---")
    st.markdown("#### 🚀 Quick Shortcuts")
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("➕ Add New Employee", use_container_width=True):
            st.session_state["menu_selection"] = "👥 Employee Management"
            st.rerun()
    with q2:
        if st.button("📅 Mark Attendance", use_container_width=True):
            st.session_state["menu_selection"] = "📅 Attendance Management"
            st.rerun()
    with q3:
        if st.button("📈 View Full Report", use_container_width=True):
            st.session_state["menu_selection"] = "📈 Attendance Report"
            st.rerun()


# -------------------------------------------------------------
# MAIN ROUTING
# -------------------------------------------------------------
if menu_option == "📊 Dashboard":
    render_dashboard()
elif menu_option == "👥 Employee Management":
    employee.render_employee_management()
elif menu_option == "📅 Attendance Management":
    attendance.render_attendance_management()
elif menu_option == "🔍 Employee Search":
    employee.render_employee_search()
elif menu_option == "📈 Attendance Report":
    attendance.render_attendance_report()
