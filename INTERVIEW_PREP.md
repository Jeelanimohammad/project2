# 🎓 HCLTech / Berribot Interview Preparation Guide
## Project: Employee Management & Attendance System
**Target Role:** Cloud Data Engineer / Data Engineer

---

## ⏱️ 1. The 60-Second Elevator Pitch

> *"I built a lightweight, full-stack **Employee Management & Attendance System** using **Python, Streamlit, SQLite, and Pandas**. The application solves the problem of manual attendance tracking and fragmented employee records.
> 
> On the backend, I designed a normalized relational database in **SQLite** consisting of an `employees` table and an `attendance` table linked via a 1-to-many Foreign Key relationship with cascade deletion. I wrote Python database functions utilizing parameterized SQL queries for complete CRUD operations—ensuring protection against SQL injection.
> 
> On the frontend, I developed an interactive web interface using **Streamlit** that features an executive KPI dashboard, employee profile management, daily attendance rosters, and dynamic search. Using **Pandas**, I automated attendance percentage calculations and department-level aggregations. 
> 
> As a Cloud Data Engineering aspirant, this project demonstrates my foundational mastery of relational data modeling, SQL queries, Python backend scripting, and end-to-end data processing."*

---

## 💡 2. Core Concepts Explained Simply

### 1. What is SQLite in simple terms?
- **SQLite** is a lightweight, serverless relational database engine.
- Unlike traditional databases like PostgreSQL or MySQL that require installing and running a separate background server, SQLite stores the entire database in a **single file on disk** (`.db`).
- It comes built right into Python’s standard library (`import sqlite3`), meaning zero configuration is required.
- **Analogy:** Traditional databases are like central filing warehouses with security guards (client-server architecture); SQLite is like a private personal notebook kept inside your backpack.

### 2. What is SQL in simple terms?
- **SQL** stands for **Structured Query Language**.
- It is the standardized domain-specific language used to communicate with relational databases to store, retrieve, update, and manage structured data organized in tables of rows and columns.
- **Analogy:** If the database is a library, SQL is the librarian who understands precise requests like *"Find all books by Author X"* or *"Add this new book to Shelf Y"*.

### 3. What is CRUD?
CRUD represents the four fundamental operations performed on persistent storage:
- **C - Create (`INSERT`):** Adding new records (e.g., adding a new employee).
- **R - Read (`SELECT`):** Fetching or querying existing data (e.g., retrieving employee listings or dashboard KPIs).
- **U - Update (`UPDATE`):** Modifying existing information (e.g., changing an employee's department or phone number).
- **D - Delete (`DELETE`):** Removing records from the database (e.g., offboarding an employee).

### 4. What are Primary Key and Foreign Key?
- **Primary Key (PK):** A column (or set of columns) that uniquely identifies every single row in a table. It cannot be NULL and cannot contain duplicates.
  - *Example in our project:* `employee_id` in the `employees` table (e.g., `EMP001`).
- **Foreign Key (FK):** A column in one table that references the Primary Key of another table, creating an explicit relationship between the two.
  - *Example in our project:* `employee_id` in the `attendance` table points to `employees.employee_id`. This prevents logging attendance for non-existent employees and enables `ON DELETE CASCADE`.

### 5. How does Python communicate with SQLite?
Python uses the built-in `sqlite3` module through a 5-step lifecycle:
1. **Connect:** `conn = sqlite3.connect("database.db")` opens a communication channel to the database file.
2. **Cursor:** `cursor = conn.cursor()` creates a cursor object, which acts as a pointer or working environment to run queries.
3. **Execute:** `cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (emp_id,))` sends the parameterized query to the engine.
4. **Commit:** `conn.commit()` permanently saves transaction modifications (`INSERT`, `UPDATE`, `DELETE`) to disk.
5. **Close:** `conn.close()` closes the connection and releases locks.

### 6. How does Streamlit work at a basic level?
- Streamlit transforms pure Python scripts into interactive web applications without requiring HTML, CSS, or JavaScript.
- **Execution Model:** Streamlit executes Python scripts from top to bottom whenever a user interacts with a widget (clicks a button, selects a dropdown, enters text).
- **State Management:** It uses `st.session_state` to retain variables across reruns.
- Widgets return values directly into Python variables (e.g., `selected_dept = st.selectbox(...)`).

### 7. How is attendance percentage calculated?
The formula is:
$$\text{Attendance Percentage (\%)} = \left(\frac{\text{Present Days}}{\text{Total Working Days}}\right) \times 100$$

- In our code (`database.py` and `attendance.py`):
  - **Present Days:** Computed via `SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END)`.
  - **Total Working Days:** Computed via `COUNT(attendance_id)`.
  - If `Total Working Days == 0`, percentage defaults to `0.0%` to prevent division-by-zero errors.

### 8. Explain the complete application flow
1. **User opens app:** `app.py` triggers `init_app()`, which calls `db.create_tables()` and seeds sample data if empty.
2. **Dashboard rendering:** `db.get_dashboard_metrics()` executes `COUNT` queries on `employees` and `attendance` for real-time KPIs.
3. **User interacts:**
   - Navigates to **Employee Management** $\rightarrow$ submits an "Add Employee" form $\rightarrow$ `db.add_employee()` issues an `INSERT` statement $\rightarrow$ database commits $\rightarrow$ Streamlit reruns and displays the updated table.
   - Navigates to **Attendance Management** $\rightarrow$ selects employee and date $\rightarrow$ `db.add_attendance()` checks for existing record and executes `UPDATE` or `INSERT`.
   - Navigates to **Attendance Report** $\rightarrow$ `db.calculate_attendance()` executes a `LEFT JOIN` and loads the dataset into a **Pandas DataFrame** $\rightarrow$ Pandas aggregates metrics and renders charts.

---

## 🎯 3. 20 Likely HCLTech / Berribot Interview Questions & Answers

### Q1: Why did you choose SQLite instead of MySQL or PostgreSQL for this project?
**Answer:** SQLite is embedded and serverless—it requires zero infrastructure setup or background daemon processes and stores the database in a single file. For a desktop/local data application, it makes the project self-contained, lightweight, and easy to run anywhere. In a cloud production environment, I would migrate this to cloud-managed PostgreSQL or Snowflake.

### Q2: What is the relationship between the `employees` and `attendance` tables?
**Answer:** It is a **One-to-Many (1:N)** relationship. One employee can have many attendance records across different dates, but each attendance entry belongs to exactly one employee. It is enforced using `employee_id` as a Foreign Key in the `attendance` table.

### Q3: Why did you use `PRAGMA foreign_keys = ON;` in SQLite?
**Answer:** By default, for backward compatibility reasons, SQLite does not enforce Foreign Key constraints. Running `conn.execute("PRAGMA foreign_keys = ON;")` explicitly enables referential integrity and activates features like `ON DELETE CASCADE`.

### Q4: How do you prevent duplicate attendance entries for the same employee on the same date?
**Answer:** I defined a composite unique constraint in the table schema: `UNIQUE(employee_id, attendance_date)`. Additionally, in `database.py`, the `add_attendance` function checks if a record exists; if it does, it updates the status; otherwise, it inserts a new record.

### Q5: How do you prevent SQL Injection in your queries?
**Answer:** I strictly avoided Python f-strings or string concatenation in queries. Instead, I used **parameterized queries** with placeholder question marks `?` (e.g., `cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (emp_id,))`). This ensures user inputs are treated as literal values, never as executable SQL code.

### Q6: What happens when an employee is deleted? What happens to their attendance records?
**Answer:** Because the foreign key is configured with `ON DELETE CASCADE`, deleting an employee from the `employees` table automatically deletes all associated attendance rows in the `attendance` table, preventing orphaned records.

### Q7: Why did you use a `LEFT JOIN` in `calculate_attendance()` instead of an `INNER JOIN`?
**Answer:** If we used an `INNER JOIN`, any newly added employee who does not have any attendance records yet would be excluded from the report. A `LEFT JOIN` ensures all employees appear in the report with 0 days logged.

### Q8: What is the purpose of `conn.commit()` in SQLite?
**Answer:** SQLite transactions are atomic. Modifications like `INSERT`, `UPDATE`, and `DELETE` happen in a temporary buffer. Calling `conn.commit()` explicitly writes the transaction permanently to disk. Read-only queries like `SELECT` do not require `commit()`.

### Q9: How does Pandas fit into this architecture when SQLite can already run SQL queries?
**Answer:** While SQL is ideal for raw data extraction and storage, Pandas provides vectorized operations, flexible aggregations (`groupby`), missing value imputation (`fillna`), and direct compatibility with Streamlit's charting and export functions (`to_csv`).

### Q10: How does Streamlit handle UI re-rendering upon button click?
**Answer:** Streamlit operates on an event-driven execution model. Any interaction (such as pressing a submit button or selecting a dropdown) triggers a rerun of the entire script from top to bottom with the updated widget state.

### Q11: How would you scale this application to handle 500,000 employees in a Cloud Data Engineering environment?
**Answer:**
1. Replace SQLite with a distributed cloud database like **Amazon Aurora PostgreSQL** or **Azure SQL Database**.
2. Partition the attendance table by year and month.
3. Add B-Tree indexes on `(employee_id, attendance_date)`.
4. Decouple reporting by generating pre-aggregated views in a Cloud Data Warehouse like **Snowflake** or **AWS Redshift**.

### Q12: How did you implement the Search feature?
**Answer:** I used the SQL `LIKE` operator with wildcard parameters (`%keyword%`) across `employee_id`, `name`, and `department`. This enables case-insensitive substring matching without requiring complex full-text search engines.

### Q13: What is the difference between `cursor.fetchone()` and `cursor.fetchall()`?
**Answer:** `fetchone()` retrieves the next single row of a query result (or `None` if no rows remain), ideal for single-record lookups or counts. `fetchall()` retrieves all remaining rows as a list of tuples, which is suitable when you need the complete result set in memory.

### Q14: How do you handle potential division by zero when calculating attendance percentage?
**Answer:** In both SQL and Pandas, I check if `total_days > 0`. If an employee has 0 recorded days, the attendance percentage is set to `0.0%` rather than dividing by zero.

### Q15: Why is modular project structure (`app.py`, `database.py`, `employee.py`, `attendance.py`) important?
**Answer:** It follows the **Separation of Concerns (SoC)** principle:
- `database.py` isolates data persistence and SQL logic.
- `employee.py` and `attendance.py` handle their respective presentation logic.
- `app.py` serves as the central router and dashboard orchestrator.
This makes the codebase testable, maintainable, and readable.

### Q16: How does `st.form` improve application performance in Streamlit?
**Answer:** Normally, every single input change triggers an immediate app rerun. Wrapping inputs in `with st.form()` bundles them together so the app only reruns once when the user clicks `st.form_submit_button`.

### Q17: What is ACID compliance, and is SQLite ACID compliant?
**Answer:** ACID stands for **Atomicity, Consistency, Isolation, and Durability**. Yes, SQLite is fully ACID compliant even through system crashes or power failures.

### Q18: What is the role of an Index in relational databases, and which columns in this project benefit from indexes?
**Answer:** An Index is a data structure (typically a B-Tree) that accelerates data retrieval without scanning every row in a table. In our system, `employees.employee_id` is automatically indexed because it is a Primary Key. An index on `attendance(attendance_date, employee_id)` significantly speeds up date-range lookups and joins.

### Q19: If multiple users access this Streamlit app concurrently, what limitation does SQLite have?
**Answer:** SQLite uses file-level locking. While multiple concurrent reads (`SELECT`) are supported, write operations (`INSERT`, `UPDATE`, `DELETE`) lock the entire database file briefly. For high-concurrency multi-user enterprise applications, a client-server RDBMS like PostgreSQL with row-level locking is required.

### Q20: How would you build an automated ETL pipeline from this system to an enterprise Data Lake?
**Answer:**
1. **Extract:** An Apache Airflow DAG or AWS Lambda function triggers daily CDC (Change Data Capture) or extracts delta attendance records via SQL.
2. **Transform:** A PySpark or dbt job cleans data, formats dates, and enriches employee dimensions.
3. **Load:** The enriched records are saved as Parquet files into **Amazon S3** or **Azure Data Lake Storage (ADLS)** and cataloged in AWS Glue / Databricks Unity Catalog for enterprise reporting.

---

## 📋 Quick Review Checklist Before Interview
- [x] Know how to explain `employees` and `attendance` table schemas.
- [x] Memorize the 60-second pitch.
- [x] Explain the formula for attendance percentage.
- [x] Be ready to explain how `sqlite3.connect` and parameterized queries work.
- [x] Be ready to discuss scaling from SQLite to PostgreSQL and Cloud Data Warehouses.
