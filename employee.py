"""
employee.py
-----------
Streamlit interface and logic for Employee Management:
- Add Employee
- View All Employees
- Update Employee Details
- Delete Employee
- Search Employees
"""

import streamlit as st
import pandas as pd
from datetime import date
import database as db

DEPARTMENTS = [
    "Engineering",
    "Data Science",
    "Human Resources",
    "Finance",
    "Marketing",
    "Quality Assurance",
    "Operations",
    "Design",
    "Sales"
]


def render_employee_management():
    """
    Renders the main Employee Management section with sub-tabs:
    - View All
    - Add Employee
    - Update Employee
    - Delete Employee
    """
    st.subheader("👥 Employee Management")
    st.caption("Manage employee records: add new hires, update profiles, view listings, or remove entries.")

    tab_view, tab_add, tab_update, tab_delete = st.tabs([
        "📋 View Employees",
        "➕ Add Employee",
        "✏️ Update Employee",
        "🗑️ Delete Employee"
    ])

    # ---------------- TAB 1: VIEW EMPLOYEES ----------------
    with tab_view:
        df_employees = db.get_employees()

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Total Registered Employees:** `{len(df_employees)}`")
        with col2:
            if not df_employees.empty:
                csv = df_employees.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export CSV",
                    data=csv,
                    file_name="employees_list.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        if df_employees.empty:
            st.info("No employees found in the database. Use the 'Add Employee' tab to register one, or seed sample data from the Dashboard.")
        else:
            st.dataframe(
                df_employees,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "employee_id": "Employee ID",
                    "name": "Full Name",
                    "department": "Department",
                    "job_role": "Job Role",
                    "email": "Email Address",
                    "phone": "Phone Number",
                    "joining_date": "Joining Date"
                }
            )

    # ---------------- TAB 2: ADD EMPLOYEE ----------------
    with tab_add:
        st.markdown("#### Register New Employee")
        with st.form(key="add_employee_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                emp_id = st.text_input("Employee ID *", placeholder="e.g. EMP011")
                name = st.text_input("Full Name *", placeholder="e.g. Jane Doe")
                dept = st.selectbox("Department *", DEPARTMENTS)
                job_role = st.text_input("Job Role *", placeholder="e.g. Software Engineer")
            with col_b:
                email = st.text_input("Email *", placeholder="e.g. jane.doe@example.com")
                phone = st.text_input("Phone Number *", placeholder="e.g. 9876543210")
                join_date = st.date_input("Joining Date *", value=date.today())

            submit_btn = st.form_submit_button("➕ Add Employee", use_container_width=True, type="primary")

            if submit_btn:
                if not emp_id.strip() or not name.strip() or not email.strip() or not phone.strip() or not job_role.strip():
                    st.error("Please fill in all required fields marked with *.")
                else:
                    success, message = db.add_employee(
                        employee_id=emp_id,
                        name=name,
                        department=dept,
                        job_role=job_role,
                        email=email,
                        phone=phone,
                        joining_date=join_date
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(f"Error: {message}")

    # ---------------- TAB 3: UPDATE EMPLOYEE ----------------
    with tab_update:
        st.markdown("#### Update Existing Employee")
        df_employees = db.get_employees()

        if df_employees.empty:
            st.warning("No employees available to update.")
        else:
            emp_options = [f"{row['employee_id']} - {row['name']}" for _, row in df_employees.iterrows()]
            selected_option = st.selectbox("Select Employee to Update", emp_options, key="select_emp_update")
            selected_id = selected_option.split(" - ")[0]

            emp_data = db.get_employee_by_id(selected_id)

            if emp_data:
                with st.form(key="update_employee_form"):
                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        st.text_input("Employee ID (Read Only)", value=emp_data["employee_id"], disabled=True)
                        u_name = st.text_input("Full Name *", value=emp_data["name"])
                        # Find index of department in DEPARTMENTS list
                        dept_idx = DEPARTMENTS.index(emp_data["department"]) if emp_data["department"] in DEPARTMENTS else 0
                        u_dept = st.selectbox("Department *", DEPARTMENTS, index=dept_idx)
                        u_role = st.text_input("Job Role *", value=emp_data["job_role"])
                    with col_u2:
                        u_email = st.text_input("Email *", value=emp_data["email"])
                        u_phone = st.text_input("Phone Number *", value=str(emp_data["phone"]))
                        try:
                            parsed_date = date.fromisoformat(emp_data["joining_date"])
                        except Exception:
                            parsed_date = date.today()
                        u_date = st.date_input("Joining Date *", value=parsed_date)

                    update_btn = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")

                    if update_btn:
                        if not u_name.strip() or not u_email.strip() or not u_phone.strip() or not u_role.strip():
                            st.error("Please fill in all required fields.")
                        else:
                            success, message = db.update_employee(
                                employee_id=selected_id,
                                name=u_name,
                                department=u_dept,
                                job_role=u_role,
                                email=u_email,
                                phone=u_phone,
                                joining_date=u_date
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(f"Error: {message}")

    # ---------------- TAB 4: DELETE EMPLOYEE ----------------
    with tab_delete:
        st.markdown("#### Delete Employee")
        st.caption("⚠️ Deleting an employee will also remove all their attendance records (via CASCADE relationship).")

        df_employees = db.get_employees()
        if df_employees.empty:
            st.warning("No employees available to delete.")
        else:
            del_options = [f"{row['employee_id']} - {row['name']} ({row['department']})" for _, row in df_employees.iterrows()]
            selected_del = st.selectbox("Select Employee to Delete", del_options, key="select_emp_delete")
            del_id = selected_del.split(" - ")[0]

            emp_data = db.get_employee_by_id(del_id)

            if emp_data:
                st.warning(f"Are you sure you want to delete **{emp_data['name']}** (`{del_id}`)? This action cannot be undone.")
                col_d1, col_d2 = st.columns([1, 3])
                with col_d1:
                    confirm_delete = st.button("🗑️ Yes, Delete", type="primary", use_container_width=True)
                if confirm_delete:
                    success, message = db.delete_employee(del_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(f"Error: {message}")


def render_employee_search():
    """
    Renders the dedicated Employee Search page.
    Allows searching by Employee ID, Name, or Department using SQL LIKE queries.
    Displays detailed profile and attendance history for matched records.
    """
    st.subheader("🔍 Employee Search")
    st.caption("Search employees by ID, Name, or Department using simple SQL queries.")

    search_query = st.text_input("Enter search keyword (e.g. 'EMP001', 'Sharma', 'Engineering'):", placeholder="Search...")

    if search_query.strip():
        results_df = db.search_employees(search_query)

        st.markdown(f"**Found `{len(results_df)}` matching records:**")

        if results_df.empty:
            st.info("No matching employees found.")
        else:
            st.dataframe(
                results_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "employee_id": "Employee ID",
                    "name": "Full Name",
                    "department": "Department",
                    "job_role": "Job Role",
                    "email": "Email Address",
                    "phone": "Phone Number",
                    "joining_date": "Joining Date"
                }
            )

            # View individual employee detail card & attendance history
            st.markdown("---")
            st.markdown("#### 👤 Detailed Employee View")
            selected_emp_id = st.selectbox(
                "Select employee to inspect attendance history:",
                results_df["employee_id"].tolist(),
                format_func=lambda x: f"{x} - {results_df.loc[results_df['employee_id'] == x, 'name'].values[0]}"
            )

            if selected_emp_id:
                emp_info = db.get_employee_by_id(selected_emp_id)
                emp_att = db.get_attendance(employee_id=selected_emp_id)

                col1, col2, col3 = st.columns(3)
                col1.metric("Employee Name", emp_info["name"])
                col2.metric("Department", emp_info["department"])
                col3.metric("Job Role", emp_info["job_role"])

                st.markdown(f"**Attendance History for `{emp_info['name']}` ({len(emp_att)} days recorded):**")
                if emp_att.empty:
                    st.info("No attendance recorded yet for this employee.")
                else:
                    st.dataframe(
                        emp_att[["attendance_date", "status"]],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "attendance_date": "Date",
                            "status": "Attendance Status"
                        }
                    )
    else:
        st.info("Type a keyword above to search through the employee directory.")
        all_df = db.get_employees()
        if not all_df.empty:
            st.caption("Currently showing all employees for quick reference:")
            st.dataframe(all_df, use_container_width=True, hide_index=True)
