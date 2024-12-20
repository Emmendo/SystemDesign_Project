# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter.messagebox import showerror
import pyodbc
import os
from datetime import datetime

# Database connection
conn = pyodbc.connect(
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=Lumine\SQLEXPRESS,1433;'
    'Database=Hills_Uni_campus;' 
    'UID=Demo_User;'
    'PWD=demo!123'  
)
cursor = conn.cursor()

# Root window for all screens
root = tk.Tk()
root.withdraw()

current_user = None
user_role = None

# Function to create the side navigation
def create_side_navigation(parent_frame):
    nav_frame = tk.Frame(parent_frame, borderwidth=1, relief="solid", padx=5, pady=5, bg="red")
    nav_frame.grid(row=0, column=0, rowspan=4, sticky="nsw", padx=10, pady=10)

    # Set the home button's command based on the user_role
    if user_role == 'teacher':
        home_button = tk.Button(nav_frame, text="Home", command=teacher_dashboard, width=15, bg="red", fg="white")
    elif user_role == 'admin':
        home_button = tk.Button(nav_frame, text="Home", command=admin_dashboard, width=15, bg="red", fg="white")
    else:
        home_button = tk.Button(nav_frame, text="Home", command=student_dashboard, width=15, bg="red", fg="white")

    home_button.pack(pady=5)

    inbox_button = tk.Button(nav_frame, text="Inbox", command=inbox_screen, width=15, bg="red", fg="white")
    inbox_button.pack(pady=5)

    logout_button = tk.Button(nav_frame, text="Logout", command=login_screen, width=15, bg="red", fg="white")
    logout_button.pack(pady=5)

# Function to create the login screen
def login_screen():
    def login():
        global current_user, user_role
        username = entry_username.get()
        password = entry_password.get()

        cursor.execute("SELECT * FROM dbo.Students WHERE Username = ? AND Password = ?", (username, password))
        student = cursor.fetchone()
        if student:
            current_user = student
            user_role = 'student'
            student_dashboard()
            return

        cursor.execute("SELECT * FROM dbo.Teachers WHERE Username = ? AND Password = ?", (username, password))
        teacher = cursor.fetchone()
        if teacher:
            current_user = teacher
            user_role = 'teacher'
            teacher_dashboard()
            return

        cursor.execute("SELECT * FROM dbo.Admins WHERE Username = ? AND Password = ?", (username, password))
        admin = cursor.fetchone()
        if admin:
            current_user = admin
            user_role = 'admin'
            admin_dashboard()
            return

        messagebox.showerror("Error", "Invalid credentials!")

    root.deiconify()
    root.title("Student Management System Login")

    root.state("zoomed")  # This maximizes the window to full screen with title bar and window controls

    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Username:").pack(pady=5)
    entry_username = tk.Entry(root)
    entry_username.pack(pady=5)

    tk.Label(root, text="Password:").pack(pady=5)
    entry_password = tk.Entry(root, show="*")
    entry_password.pack(pady=5)

    login_button = tk.Button(root, text="Login", command=login)
    login_button.pack(pady=10)

assignments_tree = None

# Function to create the student dashboard
def student_dashboard():
    global assignments_tree
    root.deiconify()
    root.title("Student Dashboard")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = int(screen_width * 0.75)
    window_height = int(screen_height * 0.75)
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    for widget in root.winfo_children():
        widget.destroy()

    # Create side navigation
    create_side_navigation(root)

    # Fetch courses for the student
    cursor.execute("SELECT DISTINCT Course, Course_Code FROM dbo.Fall_2024_Courses WHERE Student_ID = ?", current_user.Student_ID)
    courses = cursor.fetchall()

    # Dashboard Layout
    root.columnconfigure(1, weight=3)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=2)
    root.rowconfigure(2, weight=2)
    root.rowconfigure(3, weight=1)

    # Top Widgets (Inbox, Announcements, Classes)
    inbox_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(inbox_frame, text="Inbox", font=("Arial", 14, "bold")).pack()
    inbox_frame.bind("<Button-1>", lambda e: inbox_screen())
    inbox_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    announcements_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(announcements_frame, text="Instructor Announcements", font=("Arial", 14, "bold")).pack()
    tk.Label(announcements_frame, text="2", font=("Arial", 20)).pack()
    announcements_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    classes_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(classes_frame, text="Classes", font=("Arial", 14, "bold")).pack()
    classes_text = "\n".join([f"{course.Course} ({course.Course_Code})" for course in courses])
    tk.Label(classes_frame, text=classes_text, justify="left").pack()
    classes_frame.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

    # Assignments Due Soon Table
    due_assignments_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(due_assignments_frame, text="Assignments Due Soon", font=("Arial", 14, "bold")).pack()
    assignments_tree = ttk.Treeview(due_assignments_frame, columns=("Class", "Assignment", "Due Date", "Grade Value"), show="headings")
    assignments_tree.heading("Class", text="Class")
    assignments_tree.heading("Assignment", text="Assignment")
    assignments_tree.heading("Due Date", text="Due Date")
    assignments_tree.heading("Grade Value", text="Grade Value")

    # Fetch assignments due after November 2, 2024 for all grade tables
    grade_tables = ['Grades_1111', 'Grades_1122', 'Grades_1133', 'Grades_1155']
    for table in grade_tables:
        cursor.execute(f"SELECT Course_Code, Assignment_Name, Submission_Date, Points_Worth FROM dbo.{table} WHERE Student_ID = ? AND Submission_Date > '2024-11-02'", current_user.Student_ID)
        assignments_due = cursor.fetchall()
        for assignment in assignments_due:
            cursor.execute("SELECT Course FROM dbo.Fall_2024_Courses WHERE Course_Code = ?", assignment.Course_Code)
            course_name = cursor.fetchone().Course
            assignments_tree.insert("", "end", values=(course_name, assignment.Assignment_Name, assignment.Submission_Date, f"{assignment.Points_Worth} points"))

    # Pack the assignments_tree and then bind it to the double-click event
    assignments_tree.pack()
    assignments_tree.bind("<Double-1>", lambda e: open_assignment(assignments_tree, upcoming=True))
    due_assignments_frame.grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Past Assignments Section
    past_assignments_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(past_assignments_frame, text="Past Assignments", font=("Arial", 14, "bold")).pack()
    past_assignments_tree = ttk.Treeview(past_assignments_frame, columns=("Class", "Assignment", "Due Date", "Grade", "Feedback"), show="headings")
    past_assignments_tree.heading("Class", text="Class")
    past_assignments_tree.heading("Assignment", text="Assignment")
    past_assignments_tree.heading("Due Date", text="Due Date")
    past_assignments_tree.heading("Grade", text="Grade")
    past_assignments_tree.heading("Feedback", text="Feedback")

    # Fetch assignments due before or on November 2, 2024 for all grade tables
    for table in grade_tables:
        cursor.execute(f"SELECT Course_Code, Assignment_Name, Submission_Date, Assignment_Grade, Feedback FROM dbo.{table} WHERE Student_ID = ? AND Submission_Date <= '2024-11-02'", current_user.Student_ID)
        past_assignments = cursor.fetchall()
        for assignment in past_assignments:
            cursor.execute("SELECT Course FROM dbo.Fall_2024_Courses WHERE Course_Code = ?", assignment.Course_Code)
            course_name = cursor.fetchone().Course
            past_assignments_tree.insert("", "end", values=(course_name, assignment.Assignment_Name, assignment.Submission_Date, assignment.Assignment_Grade, assignment.Feedback))

    # Pack the past_assignments_tree and bind it to the double-click event
    past_assignments_tree.pack()
    past_assignments_tree.bind("<Double-1>", lambda e: open_assignment(past_assignments_tree, upcoming=False))
    past_assignments_frame.grid(row=2, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")
    # Urgent Messages Section
    urgent_messages_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(urgent_messages_frame, text="Urgent Messages", font=("Arial", 14, "bold")).pack()
    tk.Label(urgent_messages_frame, text="Scheduled Maintenance Alert 10/5/24\nBusar Bill Payment due by 10/25/24\nReview and Confirm Contact Details", justify="left").pack()
    urgent_messages_frame.grid(row=3, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Quick Chat Feature
    quick_chat_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10, bg="red")
    quick_chat_frame.grid(row=4, column=1, columnspan=3, padx=10, pady=10, sticky="sew")
    quick_chat_frame.grid_forget()  # Start minimized

    tk.Label(quick_chat_frame, text="Quick Chat", font=("Arial", 12, "bold"), fg="white", bg="red").pack(side="top", anchor="w")
    chat_thread_combobox = ttk.Combobox(quick_chat_frame)
    chat_thread_combobox.pack(pady=5)
    chat_text = tk.Text(quick_chat_frame, height=10, width=60, state="disabled")
    chat_text.pack(padx=5, pady=5)

    chat_entry = tk.Entry(quick_chat_frame, width=50)
    chat_entry.pack(side="left", padx=5, pady=5)
    send_button = tk.Button(quick_chat_frame, text="Send", command=lambda: send_quick_chat(chat_entry, chat_text, chat_thread_combobox, open_chat_button))
    send_button.pack(side="left", padx=5)

    def minimize_chat():
        quick_chat_frame.grid_forget()
        open_chat_button.grid(row=4, column=1, sticky="sew")

    def open_chat():
        quick_chat_frame.grid(row=4, column=1, columnspan=3, padx=10, pady=10, sticky="sew")
        open_chat_button.grid_forget()
        load_chat_threads(chat_thread_combobox, chat_text, open_chat_button)

    open_chat_button = tk.Button(root, text="Quick Chat", command=open_chat, bg="red", fg="white")
    open_chat_button.grid(row=4, column=1, sticky="sew")

    close_chat_button = tk.Button(quick_chat_frame, text="Minimize", command=minimize_chat, bg="red", fg="white")
    close_chat_button.pack(side="right")

    def load_chat_threads(combobox, chat_display, open_chat_button):
        cursor.execute("SELECT DISTINCT ThreadID, Subject FROM dbo.Inbox_Message WHERE Recipient1 = ? OR Sender = ?", (current_user.Student_ID, current_user.Student_ID))
        threads = cursor.fetchall()
        thread_options = list(dict.fromkeys([f"Thread {thread.ThreadID}: {thread.Subject}" for thread in threads]))  # Remove duplicates
        combobox['values'] = thread_options
        if threads:
            combobox.current(0)
            load_unread_messages(chat_display, threads[0].ThreadID, open_chat_button)

    chat_thread_combobox.bind("<<ComboboxSelected>>", lambda e: load_unread_messages(chat_text, int(chat_thread_combobox.get().split()[1].rstrip(':')), open_chat_button))
# Define path to the user's Downloads folder
DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")

# Function to upload PDF without checking for course enrollment
def upload_pdf(course_code, assignment_name):
    # Retrieve student_id from Fall_2024_Courses
    student_id = current_user.Student_ID  # Assuming current_user has been set globally after login

    # Ask for a PDF file to upload
    file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        return  # User canceled the file dialog

    # Ensure the file is a PDF
    if not file_path.endswith(".pdf"):
        messagebox.showerror("Error", "Please upload a PDF file.")
        return

    # Save the file with a unique name format in the Downloads folder
    filename = f"{student_id}_{assignment_name.replace(' ', '_')}.pdf"
    destination = os.path.join(DOWNLOAD_FOLDER, filename)
    os.rename(file_path, destination)
    
    # Update database with submission date in the relevant Grades table
    submission_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor.execute("""
            UPDATE dbo.Grades_1111
            SET Submission_submitted_Date = ?
            WHERE Course_Code = ? AND Student_ID = ? AND Assignment_Name = ?
        """, (submission_date, course_code, student_id, assignment_name))
        conn.commit()
        messagebox.showinfo("Success", "Your assignment was uploaded successfully.")
    except pyodbc.ProgrammingError as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")


# Event handler to process the PDF upload on double-click
def handle_assignment_upload(assignments_tree):
    selected_item = assignments_tree.selection()[0]  # Get selected item
    values = assignments_tree.item(selected_item, "values")
    
    course_name, assignment_name = values[0], values[1]
    
    # Fetch the course code based on the course name
    cursor.execute("SELECT Course_Code FROM dbo.Fall_2024_Courses WHERE Course = ?", course_name)
    course_code = cursor.fetchone().Course_Code
    
    # Call the upload function
    upload_pdf(course_code, current_user.Student_ID, assignment_name)

# Fetch Courses Managed Section (Hardcoded based on Teacher_ID)
def get_courses_managed(teacher_id):
    courses = []
    
    # Hardcoded courses based on Teacher_ID
    if teacher_id == 109245619:
        courses = [
            ("FA24 CSCI-C 307: Data Representation", "FA24 1122"),
            ("FA24 INFO-I 310: Multimedia Arts and Technology", "FA24 1155")
        ]
    elif teacher_id == 109245620:
        courses = [
            ("FA24 CSCI-C 201: Introduction to Programming", "FA24 1111")
        ]
    elif teacher_id == 109245621:
        courses = [
            ("FA24 INFO-C 399: Database Systems", "FA24 1133"),
            ("FA24 INFO-C 451: System Design", "FA24 1144")
        ]
    
    return courses


# Function to create the teacher dashboard
def teacher_dashboard():
    global assignments_tree
    root.deiconify()
    root.title("Teacher Dashboard")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = int(screen_width * 0.75)
    window_height = int(screen_height * 0.75)
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    for widget in root.winfo_children():
        widget.destroy()

    # Create side navigation
    create_side_navigation(root)
    
    # Dashboard Layout
    root.columnconfigure(1, weight=3)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=2)
    root.rowconfigure(2, weight=2)
    root.rowconfigure(3, weight=1)
    
    # Top Widgets (Inbox, Assignments to Grade, Classes)
    inbox_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(inbox_frame, text="Inbox", font=("Arial", 14, "bold")).pack()
    inbox_frame.bind("<Button-1>", lambda e: inbox_screen())
    inbox_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    
    # Fetch courses for the teacher
    courses = get_courses_managed(current_user.Teacher_ID)

     # Classes Managed Section
    classes_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(classes_frame, text="Classes Managed", font=("Arial", 14, "bold")).pack()
    classes_text = "\n".join([f"{course[0]} ({course[1]})" for course in courses])
    tk.Label(classes_frame, text=classes_text if classes_text else "No courses assigned.", justify="left").pack()
    classes_frame.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

     # Assignments to Grade Section
    assignments_to_grade_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(assignments_to_grade_frame, text="Assignments to Grade", font=("Arial", 14, "bold")).pack()
    num_assignments_to_grade = 0
    grade_tables = ['Grades_1111', 'Grades_1122', 'Grades_1133', 'Grades_1155']
    for table in grade_tables:
        cursor.execute(f"SELECT COUNT(*) FROM dbo.{table} WHERE Teacher_ID = ? AND Assignment_Grade IS NULL", current_user.Teacher_ID)
        num_assignments_to_grade += cursor.fetchone()[0]
    tk.Label(assignments_to_grade_frame, text=str(num_assignments_to_grade), font=("Arial", 20)).pack()
    assignments_to_grade_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
    
    closing_assignments_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(closing_assignments_frame, text="Assignments Closing Soon", font=("Arial", 14, "bold")).pack()
    assignments_tree = ttk.Treeview(closing_assignments_frame, columns=("Class", "Student", "Assignment", "Due Date", "Submission"), show="headings")
    assignments_tree.heading("Class", text="Class")
    assignments_tree.heading("Student", text="Student")
    assignments_tree.heading("Assignment", text="Assignment")
    assignments_tree.heading("Due Date", text="Due Date")
    assignments_tree.heading("Submission", text="Submission")

    grade_tables = ['Grades_1111', 'Grades_1122', 'Grades_1133', 'Grades_1155']
    for table in grade_tables:
        cursor.execute(f"""
        SELECT Course_Code, Student_ID, Assignment_Name, Submission_Date, Submission_submitted_Date
        FROM dbo.{table}
        WHERE Teacher_ID = ? AND Submission_Date > GETDATE()
    """, current_user.Teacher_ID)
        closing_assignments = cursor.fetchall()
        for assignment in closing_assignments:
            cursor.execute("SELECT Course FROM dbo.Fall_2024_Courses WHERE Course_Code = ?", assignment.Course_Code)
            course_name = cursor.fetchone().Course
            cursor.execute("SELECT Name FROM dbo.Students WHERE Student_ID = ?", assignment.Student_ID)
            student_name = cursor.fetchone().Name
            submission_status = "Submitted" if assignment.Submission_submitted_Date else "Not Submitted"
            assignments_tree.insert("", "end", values=(course_name, student_name, assignment.Assignment_Name, assignment.Submission_Date, submission_status))

    assignments_tree.pack()
    assignments_tree.bind("<Double-1>", lambda e: open_assignment(assignments_tree, upcoming=True))
    closing_assignments_frame.grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Past Assignments Section
    past_assignments_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(past_assignments_frame, text="Past Assignments", font=("Arial", 14, "bold")).pack()
    past_assignments_tree = ttk.Treeview(past_assignments_frame, columns=("Class", "Student", "Assignment", "Due Date", "Grade", "Feedback"), show="headings")
    past_assignments_tree.heading("Class", text="Class")
    past_assignments_tree.heading("Student", text="Student")
    past_assignments_tree.heading("Assignment", text="Assignment")
    past_assignments_tree.heading("Due Date", text="Due Date")
    past_assignments_tree.heading("Grade", text="Grade")
    past_assignments_tree.heading("Feedback", text="Feedback")

    for table in grade_tables:
        cursor.execute(f"""
        SELECT Course_Code, Student_ID, Assignment_Name, Submission_Date, Assignment_Grade, Feedback
        FROM dbo.{table}
        WHERE Teacher_ID = ? AND Submission_Date <= GETDATE()
    """, current_user.Teacher_ID)
        past_assignments = cursor.fetchall()
        for assignment in past_assignments:
            cursor.execute("SELECT Course FROM dbo.Fall_2024_Courses WHERE Course_Code = ?", assignment.Course_Code)
            course_name = cursor.fetchone().Course
            cursor.execute("SELECT Name FROM dbo.Students WHERE Student_ID = ?", assignment.Student_ID)
            student_name = cursor.fetchone().Name
            past_assignments_tree.insert("", "end", values=(course_name, student_name, assignment.Assignment_Name, assignment.Submission_Date, assignment.Assignment_Grade, assignment.Feedback))

    past_assignments_tree.pack()
    assignments_tree.bind("<Double-1>", lambda e: open_assignment(assignments_tree, upcoming=True))
    past_assignments_frame.grid(row=2, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")
    
    # Bind double-click event to open details
    assignments_tree.bind("<Double-1>", on_assignment_click)

# Function to open assignment details for grading
def open_assignment_details(course_code, student_name, assignment_name):
    details_window = tk.Toplevel(root)
    details_window.title(f"{assignment_name} - {student_name}")

    # Query assignment details from Assignments_1111 table
    cursor.execute("""
        SELECT Assignment_Purpose, Assignment_Content, Assignment_Rubric, Submission_Due
        FROM dbo.Assignments_1111
        WHERE Assignment_Name = ? AND Course_Code = ?
    """, (assignment_name, course_code))
    assignment_details = cursor.fetchone()

    # Display default messages if assignment details are missing
    purpose_text = assignment_details.Assignment_Purpose if assignment_details else "Purpose not available"
    content_text = assignment_details.Assignment_Content if assignment_details else "Content not available"
    rubric_text = assignment_details.Assignment_Rubric if assignment_details else "Rubric not available"
    due_date = assignment_details.Submission_Due if assignment_details else "Due date not available"

    # Frame to display assignment details
    details_frame = tk.Frame(details_window, borderwidth=1, relief="solid", padx=10, pady=10)
    details_frame.pack(fill="both", expand=True)

    tk.Label(details_frame, text=assignment_name, font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
    tk.Label(details_frame, text=f"Due: {due_date}", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)
    
    # Purpose Section
    tk.Label(details_frame, text="Purpose", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    tk.Label(details_frame, text=purpose_text, wraplength=500, justify="left").pack(anchor="w", padx=10, pady=5)
    
    # Content Section
    tk.Label(details_frame, text="Content", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    tk.Label(details_frame, text=content_text, wraplength=500, justify="left").pack(anchor="w", padx=10, pady=5)
    
    # Rubric Section
    tk.Label(details_frame, text="Rubric", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    tk.Label(details_frame, text=rubric_text, wraplength=500, justify="left").pack(anchor="w", padx=10, pady=5)
    
    # Grade and Feedback Entry Section
    tk.Label(details_frame, text="Grade", font=("Arial", 10)).pack(anchor="w", padx=10)
    grade_entry = tk.Entry(details_frame)
    grade_entry.pack(anchor="w", padx=10, pady=5)

    tk.Label(details_frame, text="Feedback", font=("Arial", 10)).pack(anchor="w", padx=10)
    feedback_entry = tk.Text(details_frame, height=4, width=50)
    feedback_entry.pack(anchor="w", padx=10, pady=5)

    # Save Button to Update Grade and Feedback
    def save_feedback():
        grade = grade_entry.get()
        feedback = feedback_entry.get("1.0", "end-1c").strip()

        # Update the relevant Grades table with feedback and grade
        cursor.execute("""
            UPDATE dbo.Grades_1111 
            SET Assignment_Grade = ?, Feedback = ?
            WHERE Course_Code = ? AND Student_ID = (SELECT Student_ID FROM dbo.Students WHERE Name = ?) AND Assignment_Name = ?
        """, (grade, feedback, course_code, student_name, assignment_name))
        conn.commit()
        showinfo("Success", "Feedback and grade saved successfully!")
        details_window.destroy()

    save_button = tk.Button(details_frame, text="Submit Grade and Feedback", command=save_feedback)
    save_button.pack(anchor="w", padx=10, pady=10)
        
# Adding event handler to Treeview
def on_assignment_click(event):
    selected_item = assignments_tree.selection()[0]  # Get selected item
    values = assignments_tree.item(selected_item, "values")
    
    # Unpack values from the selected row (assuming order is known)
    course_name, student_name, assignment_name, due_date, submission_status = values
    
    # Get course_code from database based on course_name
    cursor.execute("SELECT Course_Code FROM dbo.Fall_2024_Courses WHERE Course = ?", course_name)
    course_code = cursor.fetchone().Course_Code
    
    # Open assignment details window
    open_assignment_details(course_code, student_name, assignment_name)

    # Assuming `assignments_tree` is the Treeview object
    assignments_tree.bind("<Double-1>", on_assignment_click)

def fetch_assignments_for_teacher(teacher_id, upcoming=True):
    if upcoming:
        cursor.execute("""
            SELECT Course_Code, Student_ID, Assignment_Name, Submission_Due, Submission_submitted_Date
            FROM dbo.Assignments_1111
            WHERE Teacher_ID = ? AND Submission_Due > GETDATE()
        """, teacher_id)
    else:
        cursor.execute("""
            SELECT Course_Code, Student_ID, Assignment_Name, Submission_Due, Points_Worth,
                   Assignment_Purpose, Assignment_Content, Submission_submitted_Date
            FROM dbo.Assignments_1111
            WHERE Teacher_ID = ? AND Submission_Due <= GETDATE()
        """, teacher_id)

    assignments = cursor.fetchall()

    # Transform each assignment into a dictionary with status
    assignments_list = []
    for assignment in assignments:
        submission_status = "Awaiting Feedback" if assignment.Submission_submitted_Date else "Not Submitted"
        
        assignment_dict = {
            "Course_Code": assignment.Course_Code,
            "Student_ID": assignment.Student_ID,
            "Assignment_Name": assignment.Assignment_Name,
            "Submission_Due": assignment.Submission_Due,
            "Submission_Status": submission_status
        }

        # Additional details for past assignments if applicable
        if not upcoming:
            assignment_dict.update({
                "Points_Worth": assignment.Points_Worth,
                "Assignment_Purpose": assignment.Assignment_Purpose,
                "Assignment_Content": assignment.Assignment_Content
            })
        
        assignments_list.append(assignment_dict)

    return assignments_list

def admin_dashboard():
    root.deiconify()
    root.title("Admin Dashboard")

    # Configure window dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = int(screen_width * 0.75)
    window_height = int(screen_height * 0.75)
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Clear the root window
    for widget in root.winfo_children():
        widget.destroy()

    # Create side navigation
    create_side_navigation(root)

    # Configure grid layout for the dashboard
    root.columnconfigure(0, weight=0)  # Side navigation column
    root.columnconfigure(1, weight=3)  # Main content
    root.columnconfigure(2, weight=1)  # Quick tools
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)

    # Quick View Section (Announcements)
    quick_view_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(quick_view_frame, text="Quick View: Announcements", font=("Arial", 14, "bold")).pack(anchor="w")
    announcements_tree = ttk.Treeview(
        quick_view_frame,
        columns=("Priority", "Date", "Subject", "Roles"),
        show="headings",
    )
    announcements_tree.heading("Priority", text="Priority")
    announcements_tree.heading("Date", text="Date")
    announcements_tree.heading("Subject", text="Subject")
    announcements_tree.heading("Roles", text="Roles")

    # Hardcoded announcements data
    hardcoded_announcements = [
        ("Medium", "Oct 20, 2024", "System will be down for scheduled maintenance, service disruption possible for 30 mins", "Students, Teachers, Admins"),
        ("Low", "Oct 21, 2024", "Workshop for internship being held in main building, students are encouraged to attend.", "Students"),
    ]
    for announcement in hardcoded_announcements:
        announcements_tree.insert("", "end", values=announcement)
    announcements_tree.pack(fill="both", expand=True)
    quick_view_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Messages Section (Dynamic)
    messages_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(messages_frame, text="New Messages", font=("Arial", 14, "bold")).pack(anchor="w")
    messages_tree = ttk.Treeview(
        messages_frame,
        columns=("Sender", "Subject", "Date Sent", "ThreadID"),
        show="headings",
    )
    messages_tree.heading("Sender", text="Sender")
    messages_tree.heading("Subject", text="Subject")
    messages_tree.heading("Date Sent", text="Date Sent")
    messages_tree.heading("ThreadID", text="ThreadID")
    messages_tree.column("ThreadID", width=0, stretch=tk.NO)  # Hide ThreadID column

    # Fetch new messages for the admin
    cursor.execute("SELECT Sender, Subject, Date_Sent, ThreadID FROM dbo.Inbox_Message WHERE Recipient1 = ?", (current_user.Admin_ID,))
    messages = cursor.fetchall()
    for message in messages:
        cursor.execute("SELECT Name FROM dbo.Teachers WHERE Teacher_ID = ?", (message.Sender,))
        sender_result = cursor.fetchone()
        sender_name = sender_result.Name if sender_result else "Unknown"
        messages_tree.insert("", "end", values=(sender_name, message.Subject, message.Date_Sent, message.ThreadID))

    messages_tree.pack(fill="both", expand=True)
    messages_tree.bind("<Double-1>", lambda e: open_message_from_dashboard(messages_tree))
    messages_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    # Upcoming Meetings Section (Dynamic)
    meetings_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(meetings_frame, text="Upcoming Meetings", font=("Arial", 14, "bold")).pack(anchor="w")
    meetings_tree = ttk.Treeview(
        meetings_frame,
        columns=("Date", "Start Time", "End Time", "Overview", "Conference Type"),
        show="headings",
    )
    meetings_tree.heading("Date", text="Date")
    meetings_tree.heading("Start Time", text="Start Time")
    meetings_tree.heading("End Time", text="End Time")
    meetings_tree.heading("Overview", text="Overview")
    meetings_tree.heading("Conference Type", text="Conference Type")
    meetings_tree.column("Conference Type", width=150)

    # Fetch upcoming meetings
    cursor.execute("SELECT Day_of_Meeting, Start_Time, End_Time, Overview_of_Meeting FROM dbo.Upcoming_Meetings WHERE Admin_ID = ?", (current_user.Admin_ID,))
    meetings = cursor.fetchall()
    for meeting in meetings:
        meetings_tree.insert("", "end", values=(meeting.Day_of_Meeting, meeting.Start_Time, meeting.End_Time, meeting.Overview_of_Meeting, "Microsoft Teams"))

    meetings_tree.pack(fill="both", expand=True)
    meetings_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

    # Right-side Quick Tools Panel
    quick_tools_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(quick_tools_frame, text="Quick Tools", font=("Arial", 14, "bold")).pack(anchor="w")

    # Schedule Meeting Button
    schedule_button = tk.Button(quick_tools_frame, text="Schedule Meeting", command=lambda: print("Schedule Meeting"), width=20)
    schedule_button.pack(pady=5, fill='x')

    # Class Search Button
    class_search_button = tk.Button(quick_tools_frame, text="Class Search", command=lambda: print("Class Search"), width=20)
    class_search_button.pack(pady=5, fill='x')

    # Instructors Button
    instructors_button = tk.Button(quick_tools_frame, text="Instructors", command=lambda: print("Instructors"), width=20)
    instructors_button.pack(pady=5, fill='x')

    # Events Button
    events_button = tk.Button(quick_tools_frame, text="Events", command=lambda: print("Events"), width=20)
    events_button.pack(pady=5, fill='x')

    # Reports Button linked to reports_screen function
    reports_button = tk.Button(quick_tools_frame, text="Reports", command=reports_screen, width=20)
    reports_button.pack(pady=5, fill='x')

    quick_tools_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="nsew")


def open_message_from_dashboard(tree):
    selected_item = tree.selection()
    if not selected_item:
        print("Error: No item selected")
        return

    # Get the details of the selected message
    message_details = tree.item(selected_item, "values")
    print("Selected Message Details:", message_details)  # Debugging: Inspect message details
    if len(message_details) < 4:
        print("Error: Invalid message details")
        return

    thread_id = message_details[3]

    # Fetch all messages with the same ThreadID from Inbox_Messages table
    cursor.execute("SELECT Sender, Body, Date_Sent FROM dbo.Inbox_Message WHERE ThreadID = ?", (thread_id,))
    thread_messages = cursor.fetchall()

    # Clear current widgets
    for widget in root.winfo_children():
        widget.destroy()

    create_side_navigation(root)

    # Display the thread
    thread_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(thread_frame, text=f"Thread ID: {thread_id}", font=("Arial", 14, "bold")).pack()
    for message in thread_messages:
        cursor.execute(
            "SELECT Name FROM dbo.Teachers WHERE Teacher_ID = ? UNION SELECT Name FROM dbo.Students WHERE Student_ID = ? UNION SELECT Name FROM dbo.Admins WHERE Admin_ID = ?",
            (message.Sender, message.Sender, message.Sender),
        )
        sender_name_row = cursor.fetchone()
        sender_name = sender_name_row.Name if sender_name_row else "Unknown"
        message_frame = tk.Frame(thread_frame, borderwidth=1, relief="solid", pady=5)
        tk.Label(message_frame, text=f"{sender_name} ({message.Date_Sent})", font=("Arial", 10, "bold"), anchor="w").pack(fill="x")
        tk.Label(message_frame, text=message.Body, anchor="w").pack(fill="x")
        message_frame.pack(pady=5, fill="x")

    thread_frame.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Reply Section
    reply_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(reply_frame, text="Reply:", font=("Arial", 12)).pack()
    reply_entry = tk.Entry(reply_frame, width=50)
    reply_entry.pack(pady=5)
    send_button = tk.Button(reply_frame, text="Send", command=lambda: send_reply(reply_entry, thread_id))
    send_button.pack()
    reply_frame.grid(row=1, column=1, columnspan=3, pady=10, sticky="nsew")

    # Back Button
    back_button = tk.Button(root, text="Back", command=admin_dashboard)
    back_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")


# Display messages from the selected thread
def load_unread_messages(chat_display, thread_id, open_chat_button):
    chat_display.config(state="normal")
    chat_display.delete(1.0, tk.END)
    cursor.execute("SELECT Sender, Body, Date_Sent FROM dbo.Inbox_Message WHERE ThreadID = ?", (thread_id,))
    messages = cursor.fetchall()
    for message in messages:
        cursor.execute("SELECT Name FROM dbo.Teachers WHERE Teacher_ID = ? UNION SELECT Name FROM dbo.Students WHERE Student_ID = ?", (message.Sender, message.Sender))
        sender_name_row = cursor.fetchone()
        sender_name = sender_name_row.Name if sender_name_row else "Unknown"
        chat_display.insert(tk.END, f"{sender_name}: {message.Body}\n")
    chat_display.config(state="disabled")

    # Check if the user has replied to the thread
    cursor.execute("SELECT * FROM dbo.Inbox_Message WHERE ThreadID = ? AND Sender = ?", (thread_id, current_user.Student_ID))
    user_replied = cursor.fetchone() is not None
    quick_chat_button_text = "Quick Chat (New Messages)" if not user_replied else "Quick Chat"
    open_chat_button.config(text=quick_chat_button_text)

def send_quick_chat(entry, chat_display, chat_thread_combobox, open_chat_button):
    message = entry.get()
    if message:
        # Display the message in the chat window
        chat_display.config(state="normal")
        chat_display.insert(tk.END, f"Me: {message}\n")
        chat_display.config(state="disabled")
        entry.delete(0, tk.END)
        # Insert the message into the database for the recipient
        thread_id = int(chat_thread_combobox.get().split()[1].rstrip(':'))
        cursor.execute("INSERT INTO dbo.Inbox_Message (Message_ID, Sender, Recipient1, Subject, Body, Date_Sent, ThreadID) VALUES ((SELECT ISNULL(MAX(Message_ID), 0) + 1 FROM dbo.Inbox_Message), ?, ?, ?, ?, GETDATE(), ?)", (current_user.Student_ID, current_user.Student_ID, 'Quick Chat', message, thread_id))
        conn.commit()
        open_chat_button.config(text="Quick Chat")  # Remove notification once user has replied

# Function to create the inbox screen
def inbox_screen():
    root.deiconify()
    root.title("Inbox Messages")

    # Configure window dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = int(screen_width * 0.75)
    window_height = int(screen_height * 0.75)
    x_position = int((screen_width - window_width) / 2)
    y_position = int((screen_height - window_height) / 2)
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Create side navigation
    create_side_navigation(root)

    # Inbox Layout
    inbox_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(inbox_frame, text="Inbox Messages", font=("Arial", 14, "bold")).pack()
    messages_tree = ttk.Treeview(
        inbox_frame, columns=("Date", "Title", "Sender", "ThreadID"), show="headings"
    )
    messages_tree.heading("Date", text="Date")
    messages_tree.heading("Title", text="Title")
    messages_tree.heading("Sender", text="Sender")
    messages_tree.heading("ThreadID", text="ThreadID")

    # Fetch messages for the current user (Admin, Teacher, or Student)
    cursor.execute(
        "SELECT Message_ID, Sender, Subject, Date_Sent, ThreadID FROM dbo.Inbox_Message WHERE Recipient1 = ?",
        (current_user.Admin_ID if user_role == 'admin' else current_user.Student_ID,),
    )
    messages = cursor.fetchall()
    for message in messages:
        cursor.execute(
            "SELECT Name FROM dbo.Teachers WHERE Teacher_ID = ? UNION SELECT Name FROM dbo.Students WHERE Student_ID = ?",
            (message.Sender, message.Sender),
        )
        sender_name_row = cursor.fetchone()
        sender_name = sender_name_row.Name if sender_name_row else "Unknown"
        messages_tree.insert("", "end", values=(message.Date_Sent, message.Subject, sender_name, message.ThreadID))

    messages_tree.pack(fill="both", expand=True)
    messages_tree.bind("<Double-1>", lambda e: open_message_thread(messages_tree))
    inbox_frame.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Compose Button
    compose_button = tk.Button(root, text="Compose", command=compose_message)
    compose_button.grid(row=1, column=1, pady=10, sticky="w")

    # Back Button
    back_button = tk.Button(
        root, text="Back", command=admin_dashboard if user_role == 'admin' else student_dashboard
    )
    back_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")


# Function to open a message thread
def open_message_thread(tree):
    selected_item = tree.selection()
    if not selected_item:
        return

    message_details = tree.item(selected_item, "values")
    thread_id = message_details[3]

    # Fetch all messages with the same ThreadID from Inbox_Messages table
    cursor.execute("SELECT Sender, Body, Date_Sent FROM dbo.Inbox_Message WHERE ThreadID = ?", (thread_id,))
    thread_messages = cursor.fetchall()

    # Clear current widgets
    for widget in root.winfo_children():
        widget.destroy()

    create_side_navigation(root)

    # Display the thread
    thread_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(thread_frame, text=f"Thread ID: {thread_id}", font=("Arial", 14, "bold")).pack()
    for message in thread_messages:
        cursor.execute(
            "SELECT Name FROM dbo.Teachers WHERE Teacher_ID = ? UNION SELECT Name FROM dbo.Students WHERE Student_ID = ? UNION SELECT Name FROM dbo.Admins WHERE Admin_ID = ?",
            (message.Sender, message.Sender, message.Sender),
        )
        sender_name_row = cursor.fetchone()
        sender_name = sender_name_row.Name if sender_name_row else "Unknown"
        message_frame = tk.Frame(thread_frame, borderwidth=1, relief="solid", pady=5)
        tk.Label(message_frame, text=f"{sender_name} ({message.Date_Sent})", font=("Arial", 10, "bold"), anchor="w").pack(fill="x")
        tk.Label(message_frame, text=message.Body, anchor="w").pack(fill="x")
        message_frame.pack(pady=5, fill="x")

    thread_frame.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Reply Section
    reply_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(reply_frame, text="Reply:", font=("Arial", 12)).pack()
    reply_entry = tk.Entry(reply_frame, width=50)
    reply_entry.pack(pady=5)
    send_button = tk.Button(reply_frame, text="Send", command=lambda: send_reply(reply_entry, thread_id))
    send_button.pack()
    reply_frame.grid(row=1, column=1, columnspan=3, pady=10, sticky="nsew")

    # Back Button
    back_button = tk.Button(root, text="Back", command=inbox_screen)
    back_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# Function to send a reply
def send_reply(entry, thread_id):
    reply_text = entry.get()
    if reply_text:
        cursor.execute("INSERT INTO dbo.Inbox_Message (Message_ID, Sender, Recipient1, Subject, Body, Date_Sent, ThreadID) VALUES ((SELECT ISNULL(MAX(Message_ID), 0) + 1 FROM dbo.Inbox_Message), ?, ?, ?, ?, GETDATE(), ?)", (current_user.Student_ID, current_user.Student_ID, "Re: Thread", reply_text, thread_id))
        conn.commit()
        messagebox.showinfo("Reply Sent", "Your reply has been sent.")
        entry.delete(0, tk.END)
        inbox_screen()
    back_button = tk.Button(root, text="Back", command=student_dashboard)
    back_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# Function to compose a message
def compose_message():
    for widget in root.winfo_children():
        widget.destroy()

    create_side_navigation(root)

    compose_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(compose_frame, text="Compose Message", font=("Arial", 14, "bold")).pack()

    tk.Label(compose_frame, text="Recipient:").pack()
    recipient_combobox = ttk.Combobox(compose_frame)
    cursor.execute("SELECT Username FROM dbo.Students UNION SELECT Username FROM dbo.Teachers")
    recipients = [row.Username for row in cursor.fetchall()]
    recipient_combobox['values'] = recipients
    recipient_combobox.pack(pady=5)

    tk.Label(compose_frame, text="Subject:").pack()
    subject_entry = tk.Entry(compose_frame, width=50)
    subject_entry.pack(pady=5)

    tk.Label(compose_frame, text="Message:").pack()
    message_text = tk.Text(compose_frame, width=50, height=10)
    message_text.pack(pady=5)

    send_button = tk.Button(compose_frame, text="Send", command=lambda: send_composed_message(recipient_combobox, subject_entry, message_text))
    send_button.pack(pady=5)

    compose_frame.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Back Button
    back_button = tk.Button(root, text="Back", command=inbox_screen)
    back_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# Function to send a composed message
def send_composed_message(recipient_combobox, subject_entry, message_text):
    recipient = recipient_combobox.get()
    subject = subject_entry.get()
    message = message_text.get("1.0", tk.END).strip()
    if recipient and subject and message:
        cursor.execute("INSERT INTO dbo.Inbox_Message (Message_ID, Sender, Recipient1, Subject, Body, Date_Sent, ThreadID) VALUES ((SELECT ISNULL(MAX(Message_ID), 0) + 1 FROM dbo.Inbox_Message), ?, ?, ?, ?, GETDATE(), ?)", (current_user.Student_ID, recipient, subject, message, None))
        conn.commit()
        messagebox.showinfo("Message Sent", f"Message to '{recipient}' with subject '{subject}' has been sent.")
    else:
        messagebox.showwarning("Incomplete", "Please fill in all fields before sending.")

def open_assignment(tree, upcoming):
    global assignments_tre
    selected_item = tree.selection()
    if not selected_item:
        return

    assignment_details = tree.item(selected_item, "values")
    course_name, assignment_name = assignment_details[0], assignment_details[1]
    
    # Fetch Course_Code from the database
    cursor.execute("SELECT Course_Code FROM dbo.Fall_2024_Courses WHERE Course = ?", course_name)
    course_code = cursor.fetchone().Course_Code

    # Fetch assignment details from the database
    cursor.execute("""
        SELECT Assignment_Purpose, Assignment_Content, Assignment_Rubric, Submission_Due 
        FROM dbo.Assignments_1111 
        WHERE Assignment_Name = ? AND Course_Code = ?
    """, (assignment_name, course_code))
    assignment = cursor.fetchone()

    # Check if assignment details are available
    if not assignment:
        messagebox.showerror("Error", "Assignment details not found.")
        return

    # Clear existing widgets and set up new window
    for widget in root.winfo_children():
        widget.destroy()

    create_side_navigation(root)

    # Frame to display assignment details
    assignment_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(assignment_frame, text=f"{assignment_name}", font=("Arial", 14, "bold")).pack()
    tk.Label(assignment_frame, text=f"Due: {assignment.Submission_Due}", font=("Arial", 12)).pack()

    # Display Purpose
    tk.Label(assignment_frame, text="Purpose", font=("Arial", 12, "bold"), fg="red").pack(anchor="w")
    tk.Label(assignment_frame, text=assignment.Assignment_Purpose, wraplength=500, justify="left").pack(anchor="w", pady=5)

    # Display Content
    tk.Label(assignment_frame, text="Content", font=("Arial", 12, "bold"), fg="red").pack(anchor="w")
    tk.Label(assignment_frame, text=assignment.Assignment_Content, wraplength=500, justify="left").pack(anchor="w", pady=5)

    # Display Rubric
    tk.Label(assignment_frame, text="Rubric", font=("Arial", 12, "bold"), fg="red").pack(anchor="w")
    tk.Label(assignment_frame, text=assignment.Assignment_Rubric, wraplength=500, justify="left").pack(anchor="w", pady=5)

    # Add assignment_frame to the main grid layout
    assignment_frame.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky="nsew")

    # Update the upload button with all required arguments
    upload_button = tk.Button(root, text="Upload File (PDF only)", command=lambda: upload_pdf(course_code, assignment_name))
    upload_button.grid(row=1, column=1, columnspan=3, pady=20, sticky="s")

    # Back Button to return to dashboard
    back_button = tk.Button(root, text="Back", command=student_dashboard)
    back_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    # Ensure assignments_tree is defined and bind it to open_assignment for double-click events
    # Make sure you define assignments_tree in the student or teacher dashboard function where it's displayed
    assignments_tree.bind("<Double-1>", lambda e: open_assignment(assignments_tree, upcoming=True))

def reports_screen():
    # Display the main Reports screen with category-based options.
    for widget in root.winfo_children():
        widget.destroy()

    create_side_navigation(root)

    tk.Label(root, text="Create Report", font=("Arial", 16, "bold")).grid(row=0, column=1, padx=10, pady=10, columnspan=2)

    # Main category dropdown
    tk.Label(root, text="Select Report Type:", font=("Arial", 12)).grid(row=1, column=1, sticky="w", padx=10)
    main_category_var = tk.StringVar(value="Select a category")
    main_category_dropdown = ttk.Combobox(root, textvariable=main_category_var, state="readonly", width=20)
    main_category_dropdown['values'] = ["Students", "Teachers", "Admin"]
    main_category_dropdown.grid(row=1, column=2, sticky="w", padx=10)

    report_options_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
    report_options_frame.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="w")

    def update_report_options(event=None):
        # Update options based on selected main category.
        selected_category = main_category_var.get()
        for widget in report_options_frame.winfo_children():
            widget.destroy()

        if selected_category == "Students":
            tk.Button(report_options_frame, text="Transcript", command=transcript_screen).pack(pady=5)
            tk.Button(report_options_frame, text="Current Grades").pack(pady=5)
            tk.Button(report_options_frame, text="Past Grades").pack(pady=5)
            tk.Button(report_options_frame, text="Transferred Credits").pack(pady=5)
        elif selected_category == "Teachers":
            tk.Button(report_options_frame, text="Events").pack(pady=5)
            tk.Button(report_options_frame, text="Student Roster").pack(pady=5)
            tk.Button(report_options_frame, text="Schedule").pack(pady=5)
            tk.Button(report_options_frame, text="Semesters").pack(pady=5)
        elif selected_category == "Admin":
            tk.Button(report_options_frame, text="Maintenance").pack(pady=5)
            tk.Button(report_options_frame, text="Logs").pack(pady=5)
            tk.Button(report_options_frame, text="Database").pack(pady=5)
            tk.Button(report_options_frame, text="Back-up").pack(pady=5)

    main_category_dropdown.bind("<<ComboboxSelected>>", update_report_options)

def transcript_screen():
    # Display the Transcript Report screen.
    for widget in root.winfo_children():
        widget.destroy()

    create_side_navigation(root)

    # Header
    tk.Label(root, text="Transcript Report", font=("Arial", 16, "bold")).grid(row=0, column=1, padx=10, pady=10, columnspan=2)

    # Input for Student ID
    tk.Label(root, text="Enter Student ID Number:").grid(row=1, column=1, sticky="w", padx=10)
    student_id_entry = tk.Entry(root)
    student_id_entry.grid(row=1, column=2, padx=10)

    def fetch_transcript():
        # Fetch and display the transcript for the entered Student ID.
        student_id = student_id_entry.get()
        if not student_id:
            tk.messagebox.showerror("Error", "Please enter a valid Student ID.")
            return

        # Fetch student details
        cursor.execute("SELECT Name, Email FROM dbo.Students WHERE Student_ID = ?", (student_id,))
        student = cursor.fetchone()
        if not student:
            tk.messagebox.showerror("Error", "Student ID not found.")
            return

        # Fetch enrollment data (Past Courses and Grades)
        cursor.execute("""
            SELECT Course, Course_Code, Final_Grade 
            FROM dbo.Past_Grades 
            WHERE Student_ID = ?
        """, (student_id,))
        courses = cursor.fetchall()

        # Clear the screen and prepare for the report view
        for widget in root.winfo_children():
            widget.destroy()

        create_side_navigation(root)

        # Header
        tk.Label(root, text="Transcript Report", font=("Arial", 16, "bold")).grid(row=0, column=1, padx=10, pady=10, columnspan=2)

        # Student Details
        student_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
        student_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        tk.Label(student_frame, text="Student Details", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)
        tk.Label(student_frame, text=f"Name: {student.Name}", font=("Arial", 12)).pack(anchor="w")
        tk.Label(student_frame, text=f"Email: {student.Email}", font=("Arial", 12)).pack(anchor="w")
        tk.Label(student_frame, text=f"Student ID: {student_id}", font=("Arial", 12)).pack(anchor="w")

        # Enrollment
        courses_frame = tk.Frame(root, borderwidth=1, relief="solid", padx=10, pady=10)
        courses_frame.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        tk.Label(courses_frame, text="Enrollment", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)

        if courses:
            for course in courses:
                course_label = f"{course.Course} ({course.Course_Code}) - {course.Final_Grade}"
                tk.Label(courses_frame, text=course_label, font=("Arial", 12)).pack(anchor="w")
        else:
            tk.Label(courses_frame, text="No past courses found.", font=("Arial", 12, "italic")).pack(anchor="w")

        # "View Transcript" Button
        view_button = tk.Button(root, text="View Transcript", font=("Arial", 12), command=lambda: tk.messagebox.showinfo("Transcript", "Transcript viewed successfully."))
        view_button.grid(row=3, column=1, pady=10)

        # "Send Transcript" Button
        def send_transcript():
            # Prompt for email and send the transcript.
            email_window = tk.Toplevel(root)
            email_window.title("Send Transcript")
            tk.Label(email_window, text="Enter recipient email:", font=("Arial", 12)).pack(pady=5)
            email_entry = tk.Entry(email_window, width=30)
            email_entry.pack(pady=5)

            def confirm_send():
                recipient_email = email_entry.get()
                if not recipient_email:
                    tk.messagebox.showerror("Error", "Please enter a valid email.")
                    return
                tk.messagebox.showinfo("Success", f"Transcript sent to {recipient_email} successfully!")
                email_window.destroy()

            tk.Button(email_window, text="Send", command=confirm_send).pack(pady=5)

        send_button = tk.Button(root, text="Send Transcript", font=("Arial", 12), command=send_transcript)
        send_button.grid(row=3, column=2, pady=10)

    # Fetch Transcript Button
    fetch_button = tk.Button(root, text="Fetch Transcript", command=fetch_transcript)
    fetch_button.grid(row=1, column=3, padx=10)


def display_transcript_report(student_id):
    # Clear the main window
    for widget in root.winfo_children():
        widget.destroy()

    create_side_navigation(root)

    root.title("Transcript Report")

    # Configure grid layout
    root.columnconfigure(0, weight=0)  # Side navigation column
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)

    # Main Frame
    transcript_frame = tk.Frame(root, padx=10, pady=10)
    transcript_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Fetch student details
    cursor.execute("SELECT Name, Username FROM dbo.Students WHERE Student_ID = ?", (student_id,))
    student = cursor.fetchone()
    if not student:
        messagebox.showerror("Error", "Student not found.")
        reports_screen()
        return

    student_name, student_email = student

    # Student Details Section
    details_frame = tk.Frame(transcript_frame, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(details_frame, text="Student Details", font=("Arial", 14, "bold")).pack(anchor="w")
    tk.Label(details_frame, text=f"Name: {student_name}").pack(anchor="w")
    tk.Label(details_frame, text=f"Email: {student_email}").pack(anchor="w")
    tk.Label(details_frame, text=f"Student ID Number: {student_id}").pack(anchor="w")
    details_frame.pack(fill="x", pady=10)

    # Enrollment Section
    enrollment_frame = tk.Frame(transcript_frame, borderwidth=1, relief="solid", padx=10, pady=10)
    tk.Label(enrollment_frame, text="Enrollment", font=("Arial", 14, "bold")).pack(anchor="w")

    # Fetch grades from Past_Grades
    cursor.execute("SELECT Course, Final_Grade FROM dbo.Past_Grades WHERE Student_ID = ?", (student_id,))
    grades = cursor.fetchall()

    # Separate current and past classes
    current_classes = [grade for grade in grades if grade[1] == "In progress"]
    past_classes = [grade for grade in grades if grade[1] != "In progress"]

    # Current Classes
    if current_classes:
        tk.Label(enrollment_frame, text="Current Classes:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(5, 0))
        current_tree = ttk.Treeview(enrollment_frame, columns=("Course", "Grade"), show="headings")
        current_tree.heading("Course", text="Course")
        current_tree.heading("Grade", text="Grade")
        current_tree.column("Course", width=250)
        current_tree.column("Grade", width=100)
        for course, grade in current_classes:
            current_tree.insert("", "end", values=(course, grade))
        current_tree.pack(fill="both", expand=True, pady=5)
    else:
        tk.Label(enrollment_frame, text="No current classes.", font=("Arial", 10)).pack(anchor="w", pady=5)

    # Past Classes
    if past_classes:
        tk.Label(enrollment_frame, text="Past Classes:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
        past_tree = ttk.Treeview(enrollment_frame, columns=("Course", "Grade"), show="headings")
        past_tree.heading("Course", text="Course")
        past_tree.heading("Grade", text="Grade")
        past_tree.column("Course", width=250)
        past_tree.column("Grade", width=100)
        for course, grade in past_classes:
            past_tree.insert("", "end", values=(course, grade))
        past_tree.pack(fill="both", expand=True, pady=5)
    else:
        tk.Label(enrollment_frame, text="No past classes.", font=("Arial", 10)).pack(anchor="w", pady=5)

    enrollment_frame.pack(fill="both", expand=True, pady=10)

    # Add buttons to View/Send Transcript
    button_frame = tk.Frame(transcript_frame)
    view_button = tk.Button(button_frame, text="View Transcript", command=lambda: print("Viewing Transcript..."))
    view_button.pack(side="left", padx=10, pady=10)

    send_button = tk.Button(button_frame, text="Send Transcript", command=lambda: print("Sending Transcript..."))
    send_button.pack(side="left", padx=10, pady=10)

    button_frame.pack()

    # Back Button
    back_button = tk.Button(transcript_frame, text="Back", command=reports_screen)
    back_button.pack(side="left", padx=10, pady=10)

# Run the login screen
login_screen()
root.mainloop()