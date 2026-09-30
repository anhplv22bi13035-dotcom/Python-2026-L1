import bz2
import curses
import gzip
import json
import lzma
import math
from pathlib import Path

import numpy as np

student = []
course = []
marks = {}
ui_screen = None
DATA_FILE = Path("students.dat")
FILE_HEADER = b"STUDENTS-DATA-1\n"
COMPRESSION_METHODS = {
    "1": ("gzip", gzip.compress, gzip.decompress),
    "2": ("bz2", bz2.compress, bz2.decompress),
    "3": ("lzma", lzma.compress, lzma.decompress),
}


def show_lines(lines):
    """Show text in the terminal or in the curses screen, with paging."""
    if ui_screen is None:
        print("\n".join(str(line) for line in lines))
        return

    height, width = ui_screen.getmaxyx()
    page_size = max(1, height - 2)
    pages = [lines[index:index + page_size] for index in range(0, len(lines), page_size)] or [[]]
    for page_number, page in enumerate(pages):
        ui_screen.erase()
        ui_screen.box()
        for row, line in enumerate(page, start=1):
            ui_screen.addnstr(row, 2, str(line), max(0, width - 4))
        if page_number + 1 < len(pages):
            hint = "Press any key for next page"
        else:
            hint = "Press any key to return"
        ui_screen.addnstr(height - 2, 2, hint, max(0, width - 4))
        ui_screen.refresh()
        ui_screen.getch()


def read_value(prompt):
    """Read a line using curses when the UI is active."""
    if ui_screen is None:
        return input(prompt)

    height, width = ui_screen.getmaxyx()
    row = max(0, height - 2)
    ui_screen.move(row, 1)
    ui_screen.clrtoeol()
    ui_screen.addnstr(row, 1, prompt, max(0, width - 3))
    ui_screen.refresh()
    curses.echo()
    try:
        value = ui_screen.getstr(row, min(width - 2, len(prompt) + 1), max(1, width - len(prompt) - 3))
    finally:
        curses.noecho()
    return value.decode("utf-8").strip()


def read_number(prompt, number_type, minimum=None):
    while True:
        try:
            value = number_type(read_value(prompt))
            if minimum is not None and value < minimum:
                show_lines([f"Enter a value of at least {minimum}."])
                continue
            return value
        except ValueError:
            show_lines(["Please enter a valid number."])


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
        if not isinstance(data, dict) or not isinstance(data["student"], list) or not isinstance(data["course"], list) or not isinstance(data["marks"], dict):
            raise ValueError("Saved student data has an invalid structure.")
    except (OSError, ValueError, KeyError, IndexError, json.JSONDecodeError, EOFError, lzma.LZMAError) as error:
        show_lines([f"Could not load {DATA_FILE}: {error}"])
        return

    student = data["student"]
    course = data["course"]
    marks = data["marks"]
    show_lines([f"Loaded saved data from {DATA_FILE} using {method[0]} compression."])


def save_data():
    """Compress all application data using the selected method."""
    show_lines(["Select compression method:", "1. gzip", "2. bz2", "3. lzma"])
    while True:
        choice = read_value("Enter compression method: ")
        if choice in COMPRESSION_METHODS:
            break
        show_lines(["Invalid choice. Please select 1, 2, or 3."])

    method_name, compress, _ = COMPRESSION_METHODS[choice]
    data = json.dumps({"student": student, "course": course, "marks": marks}).encode("utf-8")
    DATA_FILE.write_bytes(FILE_HEADER + method_name.encode() + b"\n" + compress(data))
    show_lines([f"Saved data to {DATA_FILE} using {method_name} compression."])

def input_student():
    """Input student information"""
    number = read_number("Number of students: ", int, 0)
    for _ in range(number):
        student_info = {}
        student_info["id"] = read_value("Enter student ID: ")
        student_info["name"] = read_value("Enter student name: ")
        student_info["dob"] = read_value("Enter student date of birth: ")
        student.append(student_info)


def input_course():
    number = read_number("Number of courses: ", int, 0)
    for _ in range(number):
        course_info = {}
        course_info["id"] = read_value("Enter course ID: ")
        course_info["name"] = read_value("Enter course name: ")
        course_info["credits"] = read_number("Enter course credits: ", float, 0.000001)
        course.append(course_info)


def calculate_gpa(student_id):
    """Return a student's credit-weighted average, or None without marks."""
    scores = []
    credits = []
    for course_info in course:
        course_marks = marks.get(course_info["id"], {})
        if student_id in course_marks:
            scores.append(float(course_marks[student_id]))
            credits.append(float(course_info.get("credits", 1)))

    if not scores:
        return None
    return float(np.average(np.array(scores), weights=np.array(credits)))


def list_student():
    """List students from highest to lowest weighted GPA."""
    ranked_students = [(item, calculate_gpa(item["id"])) for item in student]
    ranked_students.sort(key=lambda entry: (entry[1] is None, -(entry[1] or 0)))
    lines = ["Students ranked by GPA:"]
    for item, gpa in ranked_students:
        gpa_text = f"{gpa:.2f}" if gpa is not None else "No marks"
        lines.append(f"ID: {item['id']} | {item['name']} | DOB: {item['dob']} | GPA: {gpa_text}")
    show_lines(lines)


def list_course():
    lines = ["Courses:"]
    lines.extend(f"ID: {item['id']} | {item['name']} | Credits: {item.get('credits', 1)}" for item in course)
    show_lines(lines)


def input_marks():
    """Input marks rounded down to one decimal place."""
    course_id = read_value("Enter course ID to input marks: ")
    if course_id not in [c["id"] for c in course]:
        show_lines(["Course not found."])
        return
    marks[course_id] = {}
    for s in student:
        mark = read_number(f"Enter mark for {s['name']} (ID: {s['id']}): ", float)
        mark = math.floor(mark * 10) / 10
        marks[course_id][s["id"]] = mark


def show_marks():
    """Show marks for a specific course."""
    course_id = read_value("Enter course ID to show marks: ")
    if course_id not in marks:
        show_lines(["No marks found for this course."])
        return
    lines = [f"Marks for course ID {course_id}:"]
    for student_id, mark in marks[course_id].items():
        student_name = next((s["name"] for s in student if s["id"] == student_id), "Unknown")
        lines.append(f"Student ID: {student_id} | Name: {student_name} | Mark: {mark:.1f}")
    show_lines(lines)


def show_student_gpa():
    student_id = read_value("Enter student ID: ")
    student_info = next((item for item in student if item["id"] == student_id), None)
    if student_info is None:
        show_lines(["Student not found."])
        return
    gpa = calculate_gpa(student_id)
    if gpa is None:
        show_lines([f"{student_info['name']} has no marks yet."])
        return
    show_lines([f"{student_info['name']} GPA: {gpa:.2f}"])


def main(stdscr):
    global ui_screen
    ui_screen = stdscr
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
    stdscr.keypad(True)
    load_data()
    menu_items = [
        ("Input student information", input_student),
        ("Input course information", input_course),
        ("Input marks for a course", input_marks),
        ("List students by GPA", list_student),
        ("List courses", list_course),
        ("Show marks for a course", show_marks),
        ("Calculate GPA for a student", show_student_gpa),
        ("Save and exit", None),
    ]
    selected = 0
    while True:
        stdscr.erase()
        stdscr.box()
        height, width = stdscr.getmaxyx()
        stdscr.addnstr(1, 3, "STUDENT RECORDS", max(0, width - 6), curses.color_pair(1) | curses.A_BOLD)
        for index, (label, _) in enumerate(menu_items):
            row = index + 3
            if row >= height - 2:
                break
            attribute = curses.color_pair(2) | curses.A_BOLD if index == selected else curses.A_NORMAL
            stdscr.addnstr(row, 3, f"{index + 1}. {label}", max(0, width - 6), attribute)
        stdscr.addnstr(height - 2, 3, "Use arrow keys and Enter", max(0, width - 6))
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(menu_items)
        elif key in (curses.KEY_ENTER, 10, 13):
            action = menu_items[selected][1]
            if action is None:
                save_data()
                break
            action()


if __name__ == "__main__":
    curses.wrapper(main)