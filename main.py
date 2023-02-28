from canvasapi import Canvas
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os
import pytz


# create a new course object
class Course:
    def __init__(self, course_code, assignments):
        self.course_code = course_code
        self.assignments = assignments


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

    # Create new course object for each course and add to course_list, while sorting assignments by due date
    course_list = []
    for course in courses:
        if not hasattr(course, "enrollment_term_id"):
            continue
        if course_date in course.course_code:
            assignments = course.get_assignments()
            assignment_list = []
            for assignment in assignments:
                if not hasattr(assignment, "due_at") or assignment.due_at is None:
                    continue
                if assignment.due_at_date < current_date or assignment.due_at_date > current_date + timedelta(days=7):
                    continue
                assignment_list.append(assignment)
            assignment_list.sort(key=lambda x: x.due_at_date)
            course_list.append(Course(course.course_code, assignment_list))

    # Print assignments for the next week in each course
    for course in course_list:
        print("---------------------------------")
        print(course.course_code)
        assignment_list = []
        for assignment in course.assignments:
            if not hasattr(assignment, "due_at") or assignment.due_at is None:
                continue
            if assignment.due_at_date < current_date or assignment.due_at_date > current_date + timedelta(days=7):
                continue
            assignment_list.append(assignment)

        # Print a message if there are no assignments
        if not assignment_list:
            print("\tNONE")

        # Print all assignments for the course
        for assignment in assignment_list:
            print("\t" + assignment.due_at_date.astimezone().strftime("%m/%d/%Y %H:%M:%S") + "\t" + assignment.name)

    # Sort assignments by due date ignoring the course and print
    assignment_list = []
    for course in course_list:
        for assignment in course.assignments:
            assignment_list.append(assignment)
    assignment_list.sort(key=lambda x: x.due_at_date)
    print("---------------------------------")
    print("ALL ASSIGNMENTS")
    for assignment in assignment_list:
        print("\t" + assignment.due_at_date.astimezone().strftime("%m/%d/%Y %H:%M:%S") + "\t" + assignment.name)


if __name__ == "__main__":
    main()