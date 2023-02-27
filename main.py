from canvasapi import Canvas
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import pytz

def main():
    API_URL = os.getenv("API_URL")
    API_TOKEN = os.getenv("API_TOKEN")

    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_TOKEN)
    courses = canvas.get_courses()

    # Determine the current semester
    current_date = datetime.now(timezone.utc)
    if current_date.month < 7:
        course_date = "SP" + str(current_date.year)[2:]
    else:
        course_date = "FA" + str(current_date.year)[2:]

    # Find all courses that match the current semester
    course_list = []
    for course in courses:
        if not hasattr(course, "enrollment_term_id"):
            continue
        if course_date in course.course_code:
            course_list.append(course)

    # Find all assignments for each course
    for course in course_list:
        assignments = course.get_assignments()
        print("---------------------------------")
        print(course.course_code)
        assignment_list = []
        for assignment in assignments:
            if not hasattr(assignment, "due_at") or assignment.due_at is None:
                continue
            if assignment.due_at_date < current_date or assignment.due_at_date > current_date + timedelta(days=7):
                continue
            assignment_list.append(assignment)

        # Sort the assignments by due date
        assignment_list.sort(key=lambda x: x.due_at_date)

        # Print a message if there are no assignments
        if not assignment_list:
            print("\tNONE")

        # Print all assignments for the course
        for assignment in assignment_list:
            print("\t" + assignment.due_at_date.astimezone().strftime("%m/%d/%Y %H:%M:%S") + "\t" + assignment.name)

if __name__ == "__main__":
    main()