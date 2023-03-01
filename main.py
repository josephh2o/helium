from __future__ import print_function

from canvasapi import Canvas
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import pytz

SCOPES = ['https://www.googleapis.com/auth/tasks']


# Create a course class to store values
class Course:
    def __init__(self, course_code, name, assignments):
        self.course_code = course_code
        self.name = name
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
            course_list.append(Course(course.course_code, course.name, assignment_list))

    # Default for enabling Google Tasks API
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Add tasks to appropriate task list
    try:
        service = build('tasks', 'v1', credentials=creds)

        # Check if there list a task list called "Homework". If not, create one.
        tasklists = service.tasklists().list().execute()["items"]
        for tasklist in tasklists:
            if tasklist["title"] == "Homework":
                break
            else:
                service.tasklists().insert(body={"title": "Homework"}).execute()

        # Get the task list called "Homework"
        tasklist = service.tasklists().list().execute()["items"][0]["id"]

        # Add a task for each assignment
        for course in course_list:
            for assignment in course.assignments:
                # Create a task for each assignment, and set the due date
                task = {
                    # Use only the course name
                    "title": course.name[:course.name.index(":")] + ": " + assignment.name,
                    "due": assignment.due_at_date.astimezone().isoformat()
                }
                service.tasks().insert(tasklist=tasklist, body=task).execute()

    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
