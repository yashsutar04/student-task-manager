from flask import Flask, render_template, request, redirect, session
import mysql
from db_config import get_database_connection

app = Flask(__name__)

app.secret_key = "secert123"

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        connection = get_database_connection()

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT *
            FROM users
            WHERE username = %s
            AND password = %s
        """

        cursor.execute(query, (username, password))

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        # Check if user is authenticated
        if user:

            session['user_id'] = user['user_id']
            session['full_name'] = user['full_name']

            return redirect('/')

        else:

            return render_template(
                'login.html',
                error='Invalid Username or Password'
            )

    return render_template(
        'login.html',
        error=None
    )

# Logout of the website and redirects to the logout page
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

@app.route('/')
def home():
    # Check user login


    # Create database connection
    connection = get_database_connection()

    # Create cursor object
    cursor = connection.cursor()

    # -----------------------------
    # Total Students
    # -----------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM students"
    )

    total_students = cursor.fetchone()[0]


    # -----------------------------
    # Total Tasks
    # -----------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM tasks"
    )

    total_tasks = cursor.fetchone()[0]


    # -----------------------------
    # Total Attendance Records
    # -----------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM attendance"
    )

    total_attendance = cursor.fetchone()[0]


    # -----------------------------
    # Total Task Assignments
    # -----------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM student_tasks"
    )

    total_assignments = cursor.fetchone()[0]

    # Close database connection
    cursor.close()
    connection.close()

    # Load dashboard page
    return render_template(
        'index.html',
        total_students=total_students,
        total_tasks=total_tasks,
        total_attendance=total_attendance,
        total_assignments=total_assignments
    )

@app.route('/students')
def students():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM students"
    cursor.execute(query)
    student_list = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('students.html', students=student_list)

@app.route('/add_student/', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # Retrieve form data 
    
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        mobile_number = request.form['mobile_number']
        email = request.form['email']
        course_name = request.form['course_name']

        connection = get_database_connection()
        cursor = connection.cursor()
        
        query = """
        INSERT INTO students (
           first_name, last_name, gender, mobile_number, email, course_name, admission_date
        )
        VALUES ( %s, %s, %s, %s, %s, %s, CURDATE())
        """
        
        cursor.execute(query, ( first_name, last_name, gender, mobile_number, email, course_name))
        connection.commit()
        cursor.close()
        connection.close()
        
        return redirect('/students')

    return render_template('add_student.html')
@app.route('/edit_student/<int:student_id>')
def edit_student(student_id):

    connection = get_database_connection()

    cursor = connection.cursor(dictionary=True)

    query = "SELECT * from students WHERE student_id = %s"

    cursor.execute(query,(student_id,))

    student = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template('edit_student.html',student=student)

@app.route('/update_student/<int:student_id>', methods=['POST'])
def update_student(student_id):

    first_name = request.form['first_name']
    last_name = request.form['last_name']

    connection = get_database_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        UPDATE students
         SET
            first_name = %s,
            last_name = %s
        WHERE student_id = %s
    """

    cursor.execute(
        query,
        (
            first_name,
            last_name,
            student_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect('/students')

# delete student
@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):

    connection = get_database_connection()

    cursor = connection.cursor()

    query = "DELETE FROM students WHERE student_id = %s"

    cursor.execute(query, (student_id,))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect('/students')

# Attendance Page
@app.route('/attendance')
def attendance():

    connection = get_database_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'attendance.html',
        students=students
    )

# Store attendance records in the table
@app.route('/save_attendance', methods=['POST'])
def save_attendance():

    student_id = request.form['student_id']

    attendance_status = request.form['attendance_status']

    connection = get_database_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO attendance
        (
            student_id,
            attendance_date,
            attendance_status
        )
        VALUES
        (%s, CURDATE(), %s)
    """

    cursor.execute(
        query,
        (
            student_id,
            attendance_status
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect('/attendance_report')

# Attendance Report page
@app.route('/attendance_report')
def attendance_report():

    connection = get_database_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT

            attendance.attendance_id,
            attendance.attendance_date,
            attendance.attendance_status,

            students.first_name,
            students.last_name,
            students.course_name

        FROM attendance

        INNER JOIN students
            ON attendance.student_id = students.student_id

        ORDER BY attendance.attendance_id DESC
    """

    cursor.execute(query)

    attendance_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'attendance_report.html',
        attendance_records=attendance_list
    )

# Add Task page
@app.route('/add_task', methods=['GET', 'POST'])
def add_task():


    if request.method == 'POST':

        task_name = request.form['task_name']
        task_description = request.form['task_description']
        maximum_marks = request.form['maximum_marks']

        connection = get_database_connection()

        cursor = connection.cursor()

        query = """
            INSERT INTO tasks
            (
                task_name,
                task_description,
                maximum_marks
            )
            VALUES
            (%s, %s, %s)
        """

        cursor.execute(
            query,
            (
                task_name,
                task_description,
                maximum_marks
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect('/tasks')

    return render_template("add_task.html")

# Tasks table
@app.route('/tasks')
def tasks():

    connection = get_database_connection()

    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM tasks
        ORDER BY task_id DESC
    """

    cursor.execute(query)

    task_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'tasks.html',
            tasks=task_list
        )

# Assign task to student
@app.route('/assign_task', methods=['GET', 'POST'])
def assign_task():

    # Create database connection
    connection = get_database_connection()

    # Create cursor object
    cursor = connection.cursor(dictionary=True)

    # Save assignment
    if request.method == 'POST':
        # Get form data
        student_id = request.form['student_id']
        task_id = request.form['task_id']
        submission_status = request.form['submission_status']
        obtained_marks = request.form['obtained_marks']
        remarks = request.form['remarks']

        # SQL insert query
        query = """
            INSERT INTO student_tasks
            (
                student_id,
                task_id,
                submission_status,
                obtained_marks,
                submission_date,
                remarks
            )
            VALUES
            (%s, %s, %s, %s, CURDATE(), %s)
        """

# Execute query
        cursor.execute(
            query,
            (
                student_id,
                task_id,
                submission_status,
                obtained_marks,
                remarks
            )
        )

        # Save changes
        connection.commit()

        # Redirect page
        return redirect('/student_tasks')

    # Fetch students
    cursor.execute("""
        SELECT *
        FROM students
        ORDER BY first_name ASC
    """)

    student_list = cursor.fetchall()

# Fetch tasks
    cursor.execute("""
        SELECT *
        FROM tasks
        ORDER BY task_name ASC
    """)

    task_list = cursor.fetchall()

    # Close connection
    cursor.close()
    connection.close()

    # Load page
    return render_template(
        'assign_task.html',  
        students=student_list,
        tasks=task_list
    )

# Student task report
@app.route('/student_tasks')
def student_tasks():

# Create database connection
    connection = get_database_connection()

    # Create cursor object
    cursor = connection.cursor(dictionary=True)

    # SQL query with multiple joins
    query = """
        SELECT

            student_tasks.student_task_id,
            student_tasks.submission_status,
            student_tasks.obtained_marks,
            student_tasks.submission_date,
            student_tasks.remarks,

            students.first_name,
            students.last_name,

            tasks.task_name,
            tasks.maximum_marks

        FROM student_tasks

        INNER JOIN students
            ON student_tasks.student_id = students.student_id

        INNER JOIN tasks
            ON student_tasks.task_id = tasks.task_id

        ORDER BY student_tasks.student_task_id DESC
    """

    # Execute query
    cursor.execute(query)

    # Fetch records
    task_records = cursor.fetchall()

    # Close connection
    cursor.close()
    connection.close()

    # Load page
    return render_template(
        'student_tasks.html',
        task_records=task_records
    )

# Attendance summary report
@app.route('/attendance_summary')
def attendance_summary():

    # Create database connection
    connection = get_database_connection()

    # Create cursor object
    cursor = connection.cursor(dictionary=True)

    # SQL summary query
    query = """
        SELECT

            attendance_date,

            COUNT(attendance_id)
                AS total_records,

            SUM(
                CASE
                    WHEN attendance_status = 'Present'
                    THEN 1
                    ELSE 0
                END
            ) AS total_present,

            SUM(
                CASE
                    WHEN attendance_status = 'Absent'
                    THEN 1
                    ELSE 0
                END
            ) AS total_absent,

            SUM(
                CASE
                    WHEN attendance_status = 'Leave'
                    THEN 1
                    ELSE 0
                END
            ) AS total_leave

        FROM attendance

        GROUP BY attendance_date

        ORDER BY attendance_date DESC
    """

    # Execute query
    cursor.execute(query)

    # Fetch records
    attendance_summary_records = cursor.fetchall()

    # Close connection
    cursor.close()
    connection.close()

    # Load page
    return render_template(
        'attendance_summary.html',
        attendance_summary_records=attendance_summary_records
    )

# Student performance report
@app.route('/performance_report')
def performance_report():

    # Create database connection
    connection = get_database_connection()

    # Create cursor object
    cursor = connection.cursor(dictionary=True)

    # SQL query with GROUP BY and aggregate functions
    query = """
        SELECT

            students.student_id,
            students.first_name,
            students.last_name,
            students.course_name,

            COUNT(student_tasks.student_task_id)
                AS total_tasks,

            SUM(student_tasks.obtained_marks)
                AS total_marks,

            AVG(student_tasks.obtained_marks)
                AS average_marks,

            SUM(
                CASE
                    WHEN student_tasks.submission_status = 'Submitted'
                    THEN 1
                    ELSE 0
                END
            ) AS submitted_tasks

        FROM students

        LEFT JOIN student_tasks
            ON students.student_id = student_tasks.student_id

        GROUP BY
            students.student_id,
            students.first_name,
            students.last_name,
            students.course_name

        ORDER BY total_marks DESC
    """

    # Execute query
    cursor.execute(query)

    # Fetch report data
    performance_records = cursor.fetchall()

    # Close connection
    cursor.close()
    connection.close()

    # Load report page
    return render_template(
        'performance_report.html',
        performance_records=performance_records
    )


if __name__ == '__main__':
    app.run(debug=True)