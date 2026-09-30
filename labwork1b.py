student = []
course = ()
marks = {}

def input_student():
    """Input student information"""
    global student
    while True:
        number = int(input("number of students:"))
        if number < 0:
            print("Please enter a non-negative number.")
            continue
        break
    for _ in range(number):
        student_info = {}
        student_info["id"] = input("Enter student ID: ")
        student_info["name"] = input("Enter student name: ")
        student_info["dob"] = input("Enter student date of birth: ")
        student.append(student_info)
def input_course():
    for _ in range(int(input("number of courses:"))):
        course_info = {}
        course_info["id"] = input("Enter course ID: ")
        course_info["name"] = input("Enter course name: ")
        course.append(course_info)
def list_student():
    """List all students"""
    for s in student:
        print(f"ID: {s['id']}, Name: {s['name']}, Date of Birth: {s['dob']}")
def list_course():
    for c in course:
        print(f"ID: {c['id']}, Name: {c['name']}")
def input_marks():
    """Input marks for a specific course"""
    course_id = input("Enter course ID to input marks: ")
    if course_id not in [c["id"] for c in course]:
        print("Course not found.")
        return
    marks[course_id] = {}
    for s in student:
        mark = float(input(f"Enter mark for student {s['name']} (ID: {s['id']}): "))
        marks[course_id][s["id"]] = mark
def show_marks():
    """Show marks for a specific course"""
    course_id = input("Enter course ID to show marks: ")
    if course_id not in marks:
        print("No marks found for this course.")
        return
    print(f"Marks for course ID {course_id}:")
    for student_id, mark in marks[course_id].items():
        student_name = next((s["name"] for s in student if s["id"] == student_id), "Unknown")
        print(f"Student ID: {student_id}, Name: {student_name}, Mark: {mark}")
while True:
    print(""""
    1. Input student information
    2. Input course information
    3. Input marks for a course
    4. List students
    5. List courses
    6. Show marks for a course
    7. Exit
    """)
    choice = input("Enter your choice: ")
    if choice == "1":
        input_student()
    elif choice == "2":
        input_course()
    elif choice == "3":
        input_marks()
    elif choice == "4":
        list_student()
    elif choice == "5":
        list_course()
    elif choice == "6":
        show_marks()
    elif choice == "7":
        break
    else:
        print("Invalid choice. Please try again.")