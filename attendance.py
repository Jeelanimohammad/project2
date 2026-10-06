"""
attendance.py
-------------
Streamlit interface and logic for:
1. Attendance Management (Mark Present/Absent, Daily Sheet, View Records, Search)
2. Attendance Report (Pandas data processing, calculation, percentage, analytics)
"""

import streamlit as st
import pandas as pd
from datetime import date
import database as db


def render_attendance_management():
    """
    Renders the Attendance Management section with:
    - Mark Single Attendance
    - Mark Daily Batch Attendance (Quick roster)
    - View Attendance Records (with filters by date & employee)
    """
    st.subheader("📅 Attendance Management")
    st.caption("Record and monitor daily presence and absence of employees.")

    tab_mark_single, tab_mark_batch, tab_view_records = st.tabs([
        "✏️ Mark Single Attendance",
        "📋 Quick Daily Sheet (Batch)",
        "📊 View Attendance Records"
    ])

    df_employees = db.get_employees()
    if df_employees.empty:
        st.warning("⚠️ No employees found in the database. Please add employees first before marking attendance.")
        return

    # ---------------- TAB 1: MARK SINGLE ATTENDANCE ----------------
    with tab_mark_single:
        st.markdown("#### Mark Attendance for an Employee")

        with st.form(key="mark_single_attendance_form"):
            col1, col2, col3 = st.columns(3)

            emp_options = [f"{row['employee_id']} - {row['name']} ({row['department']})" for _, row in df_employees.iterrows()]
            with col1:
                selected_emp = st.selectbox("Select Employee *", emp_options)
                emp_id = selected_emp.split(" - ")[0]

            with col2:
                att_date = st.date_input("Attendance Date *", value=date.today())

            with col3:
                status = st.selectbox("Status *", ["Present", "Absent"])

            submit_single = st.form_submit_button("💾 Save Attendance", type="primary", use_container_width=True)

            if submit_single:
                success, msg = db.add_attendance(emp_id, att_date, status)
                if success:
                    st.success(msg)
                else:
                    st.error(f"Error: {msg}")

    # ---------------- TAB 2: QUICK DAILY SHEET (BATCH) ----------------
    with tab_mark_batch:
        st.markdown("#### Quick Daily Attendance Sheet")
        st.caption("Quickly mark attendance for all employees for a selected date.")

        batch_date = st.date_input("Select Date for Daily Sheet", value=date.today(), key="batch_sheet_date")

        # Fetch existing attendance on this date if any
        existing_today = db.get_attendance(start_date=batch_date, end_date=batch_date)
        status_map = {}
        if not existing_today.empty:
            for _, row in existing_today.iterrows():
                status_map[row['employee_id']] = row['status']

        with st.form(key="batch_attendance_form"):
            st.markdown(f"**Marking attendance for:** `{batch_date}`")

            # Quick action buttons hint
            st.info("Tip: Default is 'Present'. Toggle to 'Absent' for employees who are absent.")

            batch_records = []
            for _, row in df_employees.iterrows():
                eid = row['employee_id']
                ename = row['name']
                edept = row['department']
                default_val = status_map.get(eid, "Present")
                index_val = 0 if default_val == "Present" else 1

                c1, c2, c3 = st.columns([1.5, 2.5, 2])
                with c1:
                    st.markdown(f"**{eid}**")
                with c2:
                    st.markdown(f"{ename} *({edept})*")
                with c3:
                    sel_status = st.radio(
                        f"Status for {eid}",
                        options=["Present", "Absent"],
                        index=index_val,
                        key=f"batch_status_{eid}",
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                    batch_records.append((eid, sel_status))

            submit_batch = st.form_submit_button("💾 Save All Records", type="primary", use_container_width=True)

            if submit_batch:
                success_count = 0
                for eid, st_val in batch_records:
                    s, _ = db.add_attendance(eid, batch_date, st_val)
                    if s:
                        success_count += 1
                st.success(f"Successfully recorded attendance for {success_count} employees on {batch_date}!")

    # ---------------- TAB 3: VIEW ATTENDANCE RECORDS ----------------
    with tab_view_records:
        st.markdown("#### Filter Attendance Records")

        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            emp_filter_list = ["All"] + [f"{r['employee_id']} - {r['name']}" for _, r in df_employees.iterrows()]
            selected_filter_emp = st.selectbox("Filter by Employee", emp_filter_list)
            filter_id = None if selected_filter_emp == "All" else selected_filter_emp.split(" - ")[0]

        with f_col2:
            start_d = st.date_input("From Date", value=date.today() - pd.Timedelta(days=14), key="from_d_filter")
        with f_col3:
            end_d = st.date_input("To Date", value=date.today(), key="to_d_filter")

        records_df = db.get_attendance(start_date=start_d, end_date=end_d, employee_id=filter_id)

        st.markdown(f"**Total Records Found:** `{len(records_df)}`")

        if records_df.empty:
            st.info("No attendance records found for the selected criteria.")
        else:
            col_d1, col_d2 = st.columns([3, 1])
            with col_d2:
                csv_records = records_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Records CSV",
                    data=csv_records,
                    file_name="attendance_records.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            st.dataframe(
                records_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "attendance_id": "Record ID",
                    "attendance_date": "Date",
                    "employee_id": "Employee ID",
                    "name": "Employee Name",
                    "department": "Department",
                    "status": "Status"
                }
            )


def render_attendance_report():
    """
    Renders the Attendance Report section.
    Calculates and displays:
    - Employee Name
    - Department
    - Total Working Days
    - Present Days
    - Absent Days
    - Attendance Percentage (%)
    Uses Pandas for data transformations and aggregates.
    """
    st.subheader("📈 Attendance Report & Analytics")
    st.caption("Consolidated attendance summary, percentage calculations, and department performance.")

    report_df = db.calculate_attendance()

    if report_df.empty:
        st.info("No employee or attendance data available to generate a report.")
        return

    # Filter by department
    dept_options = ["All"] + sorted(report_df["department"].unique().tolist())
    selected_dept = st.selectbox("Filter Report by Department:", dept_options)

    if selected_dept != "All":
        filtered_df = report_df[report_df["department"] == selected_dept].copy()
    else:
        filtered_df = report_df.copy()

    # Summary KPI cards for the report
    total_emp = len(filtered_df)
    total_working = filtered_df["total_days"].sum()
    total_present = filtered_df["present_days"].sum()
    total_absent = filtered_df["absent_days"].sum()
    overall_pct = round((total_present / total_working * 100), 2) if total_working > 0 else 0.0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Employees in Scope", total_emp)
    kpi2.metric("Total Present Logged", total_present)
    kpi3.metric("Total Absent Logged", total_absent)
    kpi4.metric("Average Attendance", f"{overall_pct}%")

    st.markdown("---")
    st.markdown("#### 📋 Detailed Attendance Breakdown")

    # Format dataframe for display
    display_df = filtered_df[[
        "employee_id",
        "name",
        "department",
        "total_days",
        "present_days",
        "absent_days",
        "attendance_percentage"
    ]].copy()

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn2:
        report_csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Report CSV",
            data=report_csv,
            file_name="attendance_summary_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "employee_id": "Employee ID",
            "name": "Employee Name",
            "department": "Department",
            "total_days": "Total Working Days",
            "present_days": "Present Days",
            "absent_days": "Absent Days",
            "attendance_percentage": st.column_config.ProgressColumn(
                "Attendance %",
                help="Calculated as (Present Days / Total Days) * 100",
                format="%.1f%%",
                min_value=0,
                max_value=100
            )
        }
    )

    # Department-wise Attendance Analysis using Pandas GroupBy
    st.markdown("---")
    st.markdown("#### 🏢 Department-wise Average Attendance")

    dept_summary = report_df.groupby("department").agg(
        Total_Employees=("employee_id", "count"),
        Total_Working_Days=("total_days", "sum"),
        Total_Present=("present_days", "sum"),
        Total_Absent=("absent_days", "sum")
    ).reset_index()

    dept_summary["Attendance_Percentage"] = dept_summary.apply(
        lambda r: round((r["Total_Present"] / r["Total_Working_Days"] * 100), 2) if r["Total_Working_Days"] > 0 else 0.0,
        axis=1
    )

    col_chart, col_table = st.columns([1.5, 1])
    with col_chart:
        # Streamlit bar chart
        chart_data = dept_summary.set_index("department")[["Attendance_Percentage"]]
        st.bar_chart(chart_data)
    with col_table:
        st.dataframe(
            dept_summary[["department", "Total_Employees", "Attendance_Percentage"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "department": "Department",
                "Total_Employees": "Employees",
                "Attendance_Percentage": "Avg Attendance %"
            }
        )
