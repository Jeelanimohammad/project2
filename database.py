"""
database.py
-----------
Database management module using Python's built-in sqlite3 library.
Handles all CRUD operations, table creation, relationships, and queries
for employees and attendance records.
"""

import sqlite3
import os
import pandas as pd
from datetime import date, timedelta

# Define the path to the SQLite database file
DB_DIR = os.path.join(os.path.dirname(__file__), "database")
DB_PATH = os.path.join(DB_DIR, "employee_management.db")


def get_connection():
    """
    Establish and return a connection to the SQLite database.
    Ensures foreign key constraints are enabled.
    """
    # Ensure database directory exists
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    # Enable foreign key support in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_tables():
    """
    Create 'employees' and 'attendance' tables if they do not exist.
    'employee_id' acts as Primary Key in employees and Foreign Key in attendance.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Table 1: employees
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            job_role TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            joining_date TEXT NOT NULL
        );
    """)

    # Table 2: attendance
    # Uses employee_id as Foreign Key linked to employees(employee_id)
    # UNIQUE(employee_id, attendance_date) ensures one status per employee per day
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
            FOREIGN KEY (employee_id) REFERENCES employees (employee_id) ON DELETE CASCADE,
            UNIQUE (employee_id, attendance_date)
        );
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------------------
# EMPLOYEE CRUD OPERATIONS
# -------------------------------------------------------------

def add_employee(employee_id, name, department, job_role, email, phone, joining_date):
    """
    Insert a new employee record into the 'employees' table.
    Returns (True, message) on success or (False, error_message) on failure.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO employees (employee_id, name, department, job_role, email, phone, joining_date)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        cursor.execute(query, (
            employee_id.strip(),
            name.strip(),
            department.strip(),
            job_role.strip(),
            email.strip(),
            phone.strip(),
            str(joining_date)
        ))
        conn.commit()
        conn.close()
        return True, f"Employee {name} ({employee_id}) added successfully!"
    except sqlite3.IntegrityError:
        return False, f"Employee ID '{employee_id}' already exists."
    except Exception as e:
        return False, str(e)


def get_employees():
    """
    Fetch and return all employee records as a Pandas DataFrame.
    Uses a simple SELECT query.
    """
    conn = get_connection()
    query = """
        SELECT employee_id, name, department, job_role, email, phone, joining_date
        FROM employees
        ORDER BY employee_id ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_employee_by_id(employee_id):
    """
    Fetch a single employee's record by employee_id.
    Returns a dictionary or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT employee_id, name, department, job_role, email, phone, joining_date
        FROM employees
        WHERE employee_id = ?;
    """
    cursor.execute(query, (employee_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "employee_id": row[0],
            "name": row[1],
            "department": row[2],
            "job_role": row[3],
            "email": row[4],
            "phone": row[5],
            "joining_date": row[6]
        }
    return None


def update_employee(employee_id, name, department, job_role, email, phone, joining_date):
    """
    Update details of an existing employee in the 'employees' table.
    Uses a simple UPDATE query.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE employees
            SET name = ?,
                department = ?,
                job_role = ?,
                email = ?,
                phone = ?,
                joining_date = ?
            WHERE employee_id = ?;
        """
        cursor.execute(query, (
            name.strip(),
            department.strip(),
            job_role.strip(),
            email.strip(),
            phone.strip(),
            str(joining_date),
            employee_id.strip()
        ))
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()

        if affected_rows > 0:
            return True, f"Employee {employee_id} updated successfully!"
        else:
            return False, f"Employee ID {employee_id} not found."
    except Exception as e:
        return False, str(e)


def delete_employee(employee_id):
    """
    Delete an employee and their related attendance records.
    Uses a simple DELETE query.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM employees WHERE employee_id = ?;"
        cursor.execute(query, (employee_id.strip(),))
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()

        if affected_rows > 0:
            return True, f"Employee {employee_id} deleted successfully!"
        else:
            return False, f"Employee ID {employee_id} not found."
    except Exception as e:
        return False, str(e)


def search_employees(search_term):
    """
    Search employees by employee_id, name, or department using SQL LIKE operator.
    """
    conn = get_connection()
    query = """
        SELECT employee_id, name, department, job_role, email, phone, joining_date
        FROM employees
        WHERE employee_id LIKE ? 
           OR name LIKE ? 
           OR department LIKE ?
        ORDER BY employee_id ASC;
    """
    wildcard = f"%{search_term.strip()}%"
    df = pd.read_sql_query(query, conn, params=(wildcard, wildcard, wildcard))
    conn.close()
    return df


# -------------------------------------------------------------
# ATTENDANCE OPERATIONS
# -------------------------------------------------------------

def add_attendance(employee_id, attendance_date, status):
    """
    Mark or update attendance for an employee on a given date.
    If attendance for that employee and date already exists, it updates it.
    Otherwise, it inserts a new record.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if record already exists for this employee and date
        check_query = "SELECT attendance_id FROM attendance WHERE employee_id = ? AND attendance_date = ?;"
        cursor.execute(check_query, (employee_id, str(attendance_date)))
        existing = cursor.fetchone()

        if existing:
            # Update existing record
            update_query = "UPDATE attendance SET status = ? WHERE employee_id = ? AND attendance_date = ?;"
            cursor.execute(update_query, (status, employee_id, str(attendance_date)))
            msg = f"Attendance updated to '{status}' for {employee_id} on {attendance_date}."
        else:
            # Insert new record
            insert_query = """
                INSERT INTO attendance (employee_id, attendance_date, status)
                VALUES (?, ?, ?);
            """
            cursor.execute(insert_query, (employee_id, str(attendance_date), status))
            msg = f"Attendance marked as '{status}' for {employee_id} on {attendance_date}."

        conn.commit()
        conn.close()
        return True, msg
    except Exception as e:
        return False, str(e)


def get_attendance(start_date=None, end_date=None, employee_id=None):
    """
    Fetch attendance records joined with employee names and departments.
    Uses a basic SQL JOIN between 'attendance' and 'employees'.
    """
    conn = get_connection()
    query = """
        SELECT 
            a.attendance_id,
            a.attendance_date,
            a.employee_id,
            e.name,
            e.department,
            a.status
        FROM attendance a
        JOIN employees e ON a.employee_id = e.employee_id
        WHERE 1=1
    """
    params = []
    if start_date:
        query += " AND a.attendance_date >= ?"
        params.append(str(start_date))
    if end_date:
        query += " AND a.attendance_date <= ?"
        params.append(str(end_date))
    if employee_id and employee_id != "All":
        query += " AND a.employee_id = ?"
        params.append(employee_id)

    query += " ORDER BY a.attendance_date DESC, a.employee_id ASC;"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def calculate_attendance():
    """
    Calculate summary attendance statistics for every employee:
    - Employee ID
    - Employee Name
    - Department
    - Total Working Days (total marked days)
    - Present Days
    - Absent Days
    - Attendance Percentage (%)
    Uses simple SQL JOIN and aggregation, with Pandas processing.
    """
    conn = get_connection()
    query = """
        SELECT 
            e.employee_id,
            e.name,
            e.department,
            COUNT(a.attendance_id) AS total_days,
            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_days,
            SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS absent_days
        FROM employees e
        LEFT JOIN attendance a ON e.employee_id = a.employee_id
        GROUP BY e.employee_id, e.name, e.department
        ORDER BY e.employee_id ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Clean null counts if employee has 0 attendance records
    df['total_days'] = df['total_days'].fillna(0).astype(int)
    df['present_days'] = df['present_days'].fillna(0).astype(int)
    df['absent_days'] = df['absent_days'].fillna(0).astype(int)

    # Calculate Attendance Percentage: (Present Days / Total Days) * 100
    df['attendance_percentage'] = df.apply(
        lambda row: round((row['present_days'] / row['total_days'] * 100), 2) if row['total_days'] > 0 else 0.0,
        axis=1
    )

    return df


# -------------------------------------------------------------
# DASHBOARD METRICS & SEEDING HELPERS
# -------------------------------------------------------------

def get_dashboard_metrics(target_date=None):
    """
    Get key summary numbers for the main dashboard:
    1. Total Employees
    2. Present Today (on target_date)
    3. Absent Today (on target_date)
    4. Average Attendance % across the organization
    """
    if target_date is None:
        target_date = str(date.today())
    else:
        target_date = str(target_date)

    conn = get_connection()
    cursor = conn.cursor()

    # 1. Total Employees count
    cursor.execute("SELECT COUNT(*) FROM employees;")
    total_employees = cursor.fetchone()[0]

    # 2. Present Today
    cursor.execute("""
        SELECT COUNT(*) FROM attendance 
        WHERE attendance_date = ? AND status = 'Present';
    """, (target_date,))
    present_today = cursor.fetchone()[0]

    # 3. Absent Today
    cursor.execute("""
        SELECT COUNT(*) FROM attendance 
        WHERE attendance_date = ? AND status = 'Absent';
    """, (target_date,))
    absent_today = cursor.fetchone()[0]

    conn.close()

    # 4. Average Attendance % across all employees
    attendance_report = calculate_attendance()
    if not attendance_report.empty and attendance_report['total_days'].sum() > 0:
        total_present = attendance_report['present_days'].sum()
        total_marked = attendance_report['total_days'].sum()
        avg_percentage = round((total_present / total_marked) * 100, 2)
    else:
        avg_percentage = 0.0

    return {
        "total_employees": total_employees,
        "present_today": present_today,
        "absent_today": absent_today,
        "average_attendance": avg_percentage,
        "target_date": target_date
    }


def seed_sample_data():
    """
    Populates database with sample employee data from sample_data/employees.csv
    and generates 14 days of realistic attendance records.
    """
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM employees;")
    count = cursor.fetchone()[0]
    conn.close()

    if count > 0:
        return False, "Database already has records. Seeding skipped."

    csv_path = os.path.join(os.path.dirname(__file__), "sample_data", "employees.csv")
    if not os.path.exists(csv_path):
        return False, "sample_data/employees.csv not found."

    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        add_employee(
            row["employee_id"],
            row["name"],
            row["department"],
            row["job_role"],
            row["email"],
            str(row["phone"]),
            str(row["joining_date"])
        )

    # Generate attendance for the past 10 working days
    today = date.today()
    employees_df = get_employees()
    emp_ids = employees_df["employee_id"].tolist()

    for i in range(10, -1, -1):
        day = today - timedelta(days=i)
        # Skip Sundays
        if day.weekday() == 6:
            continue
        for idx, emp_id in enumerate(emp_ids):
            # Realistic presence: most present, occasional absent
            if (idx + i) % 7 == 0:
                status = "Absent"
            else:
                status = "Present"
            add_attendance(emp_id, str(day), status)

    return True, f"Successfully seeded {len(df)} employees and 10 days of attendance!"
