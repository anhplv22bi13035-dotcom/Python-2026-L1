import bz2
import gzip
import json
import lzma
from pathlib import Path

student = []
course = []
marks = {}
DATA_FILE = Path("students.dat")
FILE_HEADER = b"STUDENTS-DATA-1\n"
COMPRESSION_METHODS = {
    "1": ("gzip", gzip.compress, gzip.decompress),
    "2": ("bz2", bz2.compress, bz2.decompress),
    "3": ("lzma", lzma.compress, lzma.decompress),
}


def load_data():
    """Load saved student data when a data file is available."""
    global student, course, marks
    if not DATA_FILE.exists():
        return

    try:
        contents = DATA_FILE.read_bytes()
        if not contents.startswith(FILE_HEADER):
            raise ValueError("Unrecognized data file format.")
        method_name, compressed_data = contents[len(FILE_HEADER):].split(b"\n", 1)
        method = next(
            (entry for entry in COMPRESSION_METHODS.values() if entry[0].encode() == method_name),
            None,
        )
        if method is None:
            raise ValueError("Unsupported compression method.")
        data = json.loads(method[2](compressed_data).decode("utf-8"))
        if not isinstance(data["student"], list) or not isinstance(data["course"], list) or not isinstance(data["marks"], dict):
            raise ValueError("Saved student data has an invalid structure.")
    except (OSError, ValueError, KeyError, IndexError, json.JSONDecodeError, EOFError, lzma.LZMAError) as error:
        print(f"Could not load {DATA_FILE}: {error}")
        return

    student = data["student"]
    course = data["course"]
    marks = data["marks"]
    print(f"Loaded saved data from {DATA_FILE} using {method[0]} compression.")


def save_data():
    """Compress all application data using the selected method."""
    print("Select compression method:")
    print("1. gzip\n2. bz2\n3. lzma")
    while True:
        choice = input("Enter compression method: ")
        if choice in COMPRESSION_METHODS:
            break
        print("Invalid choice. Please select 1, 2, or 3.")

    method_name, compress, _ = COMPRESSION_METHODS[choice]
    data = json.dumps({"student": student, "course": course, "marks": marks}).encode("utf-8")
    DATA_FILE.write_bytes(FILE_HEADER + method_name.encode() + b"\n" + compress(data))
    print(f"Saved data to {DATA_FILE} using {method_name} compression.")

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
def main():
    load_data()
    while True:
        print("""
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
            save_data()
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()