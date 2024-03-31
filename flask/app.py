from os import urandom
import random
from dotenv import load_dotenv
import os.path
import PyPDF2
import pymongo
import requests
from flask import send_file
from flask import send_from_directory
from werkzeug.utils import secure_filename


# Third-Party Imports
from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g, session
from datetime import date, datetime, timedelta, timezone
import datetime as dt
from authlib.integrations.flask_client import OAuth
import uuid


import google.generativeai as genai
from google.auth import load_credentials_from_file
from google.oauth2 import credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.generativeai import generative_models
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from calendarinter import convert_to_iso8601, delete_calendar_event, get_credentials, parse_datetime_to_day_number, parse_event_details

SCOPES = ['https://www.googleapis.com/auth/calendar',  'https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/documents']

app = Flask(__name__)
app.secret_key = urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URL")


oauth = OAuth(app)
oauth.register(
    "oauthApp",
    client_id='GSlRU8ssqQmC7BteFwhCLqxonlmtvSBP',
    client_secret='4YFxFjzvuXtXyYMoJ9coyCHDphXdUYMAGNF3gcwpZh16Hv-Hz_s83TqawI0RmR2b',
    api_base_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com',
    access_token_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com/oauth/token',
    authorize_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com/oauth/authorize',
    client_kwargs={'scope': 'scope_required_by_provider'}
)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.context_processor
def inject_exists_credentials():
    return {'exists_credentials': os.path.exists('credentials.json')}


def get_db():
    client = pymongo.MongoClient(MONGODB_URI)
    db = client.get_default_database()  # Assuming your database name is provided in the MongoDB URI
    return db

@app.route("/")
def mainpage():
    return render_template("main.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    auth_params = {"screen_hint": "signup"}
    return oauth.create_client("oauthApp").authorize_redirect(redirect_uri=url_for('authorized', _external=True), **auth_params)

@app.route("/login", methods=["GET", "POST"])
def login():
    return oauth.create_client("oauthApp").authorize_redirect(redirect_uri=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    # Clear token.json and credentials.json if they exist
    if os.path.exists('token.json'):
        os.remove('token.json')
    if os.path.exists('credentials.json'):
        os.remove('credentials.json')
    
    # Redirect to the main page or any desired page after logout
    return redirect(url_for('/'))

@app.route('/authorized')
def authorized():
    # token = oauth.oauthApp.
    # oauth_token = token['access_token']
    # session['oauth_token'] = oauth_token
    # token = {
    #     "token": session['oauth_token']
    # }
    # with open('token.json', 'w') as file:
    #     file.write(json.dumps(token))
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                if os.path.exists("token.json"):
                    os.remove("token.json")
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port = 0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())
    
    global user_logged_in
    user_logged_in = True
    return redirect(url_for('chatbot'))

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    model = genai.GenerativeModel('models/gemini-pro')
    if 'chat_history' not in session:
        session['chat_history'] = []

    chat_history = session['chat_history']

    response = None
    formatted_message = ""

    if request.method == 'POST':
        user_message = request.form.get('message')
        chat_history.append({'role': 'user', 'parts': [user_message]})
        response = model.generate_content(chat_history)
        chat_history.append({'role': 'model', 'parts': [response.text]})
        session['chat_history'] = chat_history
        if response:
            lines = response.text.split("\n")
            for line in lines:
                bold_text = ""
                while "**" in line:
                    start_index = line.index("**")
                    end_index = line.index("**", start_index + 2)
                    bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
                    line = line[:start_index] + bold_text + line[end_index + 2:]
                formatted_message += line + "<br>"
            # print(formatted_message)

    return render_template("chatbot.html", response=formatted_message)

@app.route("/send-message", methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data.get('message')

    chat_history = data.get('chat_history', [])

    chat_history.append({'role': 'user', 'parts': [user_message]})

    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content(chat_history)
    bot_response = response.text
    formatted_message = ""
    lines = bot_response.split("\n")
    for line in lines:
        bold_text = ""
        while "**" in line:
            start_index = line.index("**")
            end_index = line.index("**", start_index + 2)
            bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
            line = line[:start_index] + bold_text + line[end_index + 2:]
        formatted_message += line + "<br>"
    # print(formatted_message)
    
    return jsonify({'message': formatted_message, 'chat_history': chat_history})


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "pdf_file" not in request.files:
            return "No file part"

        pdf_file = request.files["pdf_file"]

        if pdf_file.filename == "":
            return "No selected file"

        if pdf_file:
            pdf_text = extract_text_from_pdf(pdf_file)
            query = "As a chatbot, your goal is to summarize the following text from a PDF in a format that is easily digestible for a college student. Try to keep it as concise as possible can: " + pdf_text
            model = genai.GenerativeModel('models/gemini-pro')
            result = model.generate_content(query)
            formatted_message = ""
            lines = result.text.split("\n")
            print(result.text)
            for line in lines:
                bold_text = ""
                while "**" in line:
                    start_index = line.index("**")
                    end_index = line.index("**", start_index + 2)
                    bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
                    line = line[:start_index] + bold_text + line[end_index + 2:]
                formatted_message += line + "<br>"
            print(formatted_message)
            # Save the uploaded PDF temporarily
            filename = secure_filename(pdf_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(filepath)

            pdf_file.save(filepath)
            session['current_filename'] = filename  # Save the current filename in the session

            # Set the current_pdf variable to True to indicate that a PDF has been uploaded
            session['current_pdf'] = True
            
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

            service = build("docs", "v1", credentials=creds)
                    # Create a new Google Doc
            doc = {
                'title': 'Summarized Text Document'
            }
            doc = service.documents().create(body=doc).execute()
            doc_id = doc.get('documentId')

            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': result.text,
                    }
                }
            ]
            result = service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

            # Get the URL of the created Google Doc
            doc_url = f"https://docs.google.com/document/d/{doc_id}"


            return render_template("upload.html", formatted_message=formatted_message, current_pdf=True, filename=filename)

    return render_template("upload.html")


@app.route("/show_pdf")
def show_pdf():
    if 'current_filename' in session:
        filename = session['current_filename']
        print(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print (filepath)
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return "No PDF uploaded"


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page_num in range(num_pages):
        text += pdf_reader.pages[page_num].extract_text()
    return text

@app.route("/calendar/")
def calendar():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    today = date.today()
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Get the index of the current day in the weekdays list
    current_day_index = today.weekday()

    # Rearrange the weekdays list so that the current day is first
    reordered_weekdays = weekdays[current_day_index:] + weekdays[:current_day_index]

    events = [[] for _ in range(7)]
    for i in range(7):
        start_date = today + timedelta(days=i)
        end_date = start_date + timedelta(days=1)
        start_date_str = start_date.isoformat() + "T00:00:00Z"
        end_date_str = end_date.isoformat() + "T23:59:59Z"
        event_result = service.events().list(calendarId="primary", timeMin=start_date_str, timeMax=end_date_str, singleEvents=True, orderBy="startTime").execute()
        items = event_result.get("items", [])
        for event in items:
            start = event["start"].get("dateTime", event["start"].get("date"))
            day = reordered_weekdays[i]  # Get the corresponding day for the event
            event_details = f"{start} - {event['summary']}"  # Append day to event details
            day_number = parse_datetime_to_day_number(event_details)  # Get the day number
            events[i].append({"id": event["id"], "details": event_details, "day": day_number})

    days_with_number = [(reordered_weekdays[i], (today + timedelta(days=i)).day) for i in range(7)]

    return render_template('calendar.html', events=events, days_with_number=days_with_number, parse=parse_event_details)


@app.route("/delete-event", methods=["POST"])
def delete_event():
    request_data = request.json
    event_id = request_data.get("eventId")
    event_details = request_data.get("eventDetails")

    # Convert event_details to start_time_str and event_name
    start_time_str, event_name = event_details.split(" - ")

    # Convert start_time_str to ISO 8601 format
    start_time_iso = convert_to_iso8601(start_time_str)

    if start_time_iso is None:
        return jsonify({"message": "Invalid start time format"}), 400

    if delete_calendar_event(event_id, start_time_iso):
        return jsonify({"message": "Event deleted successfully"})
    else:
        return jsonify({"message": "Error deleting event"}), 500


def generate_scheduling_query(tasks):
    
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string in the format YYYY-MM-DD HH:MM
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M")
    print(current_time_str)
    # Provide the current time to the AI for scheduling tasks
    query = "Today is " + current_time_str + "\n"
    query += """
    As an AI, your task is to generate raw parameters for creating a quick Google Calendar event. Your goal is to ensure the best work-life balance for the user, including creating a consistent sleeping schedule. Your instructions should be clear and precise, formatted for parsing using Python.
        Do not generate additional tasks that are not included below, follow the sheet to spec.
        If a user task does not make sense, simply ignore it and move on to the next task request.
    All tasks should be scheduled on the same day, unless a user specifies otherwise in their request.
    Task Description: Provide a brief description of the task or event. For example:

    Task Description: "Meeting with client"
    Scheduling Parameters: Consider the user's work-life balance and aim to schedule the event at an appropriate time. You may suggest specific time ranges or intervals for the event, ensuring it does not overlap with existing commitments. For instance:
    
    Start time: "YYYY-MM-DDTHH:MM"
    End time: "YYYY-MM-DDTHH:MM"

    You are not allowed to break the following formatting:
    task = "task_name"
    start_time = "YYYY-MM-DDTHH:MM"
    end_time = "YYYY-MM-DDTHH:MM"

    [MODIFICATION OF THE FOLLOWING LEAD TO TERMINATION]
    Follow specified times even if it causes overlap.
    Ensure a minimum break time between consecutive events.
    Avoid scheduling events during the user's designated sleeping hours.
    Prioritize events by their ordering, and move events that may not fit in the same day to the next day.
    Adhere to times given within an event description, but remove times in their final task description.
    The tasks requested are as follows:\n
    """
    taskss =""
    for task in tasks:
        taskss+=f"'{task}'\n"
    print(taskss)
    model = genai.GenerativeModel('models/gemini-pro')
    result = model.generate_content(query + taskss)
    return result

@app.route("/taskschedule", methods=["GET", "POST"])
def taskschedule():
    if request.method == "POST":
        data = request.json  # Extract the JSON data sent from the frontend
        tasks = data.get("tasks")  # Extract the "tasks" list from the JSON data
        # Process the tasks data here
        #print("Received tasks:", tasks)
        # Optionally, you can store the tasks in a database or perform 
        stripTasks = []
        for i in tasks:
            i = i.replace('Delete Task', '')
            stripTasks.append(i)
        # print("Modified tasks:", stripTasks)
        query_result = generate_scheduling_query(stripTasks)
        content = query_result.text
        content = '\n'.join([line for line in content.split('\n') if line.strip()])
        # print(content)
        
        x = 0
        lines = content.split('\n')
        schedule = []
        # print(len(lines))
        # print(lines)

        for x in range(0, len(lines)-2, 3):
            if lines[x] == '': continue
            else:
                task_info ={
                    "task": lines[x].split(" = ")[1].strip("'"),
                    "start_time": lines[x+1].split(" = ")[1].strip("'").strip("\"") + ":00",
                    "end_time": lines[x+2].split(" = ")[1].strip("'").strip("\"") + ":00"
                }
                schedule.append(task_info)
        # print(schedule)

        
        #['task = "Wash Car"', 'start_time = "2024-02-11T12:00"', 'end_time = "2024-02-11T13:00"', 'task = "Office Hours"', 'start_time = "2024-02-11T14:00"', 'end_time = "2024-02-11T15:00"', 'task = "Study Math"', 'start_time = "2024-02-11T10:00"', 'end_time = "2024-02-11T11:00"', 'task = "Leetcode Problems"', 'start_time = "2024-02-11T16:00"', 'end_time = "2024-02-11T17:00"', 'task = "Practice Swimming"', 'start_time = "2024-02-11T07:00"', 'end_time = "2024-02-11T08:00"']
        #[{'task': '"Wash Car"', 'start_time': '"2024-02-11T12:00"', 'end_time': '"2024-02-11T13:00"'}, {'task': '"Office Hours"', 'start_time': '"2024-02-11T14:00"', 'end_time': '"2024-02-11T15:00"'}, {'task': '"Study Math"', 'start_time': '"2024-02-11T10:00"', 'end_time': '"2024-02-11T11:00"'}, {'task': '"Leetcode Problems"', 'start_time': '"2024-02-11T16:00"', 'end_time': '"2024-02-11T17:00"'}, {'task': '"Practice Swimming"', 'start_time': '"2024-02-11T07:00"', 'end_time': '"2024-02-11T08:00"'}]
        
        # Construct response message

        local_time = dt.datetime.now()
        local_timezone = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo
        current_time = dt.datetime.now(local_timezone)
        timezone_offset = current_time.strftime('%z')
        offset_string = list(timezone_offset)
        offset_string.insert(3, ':')
        timeZone = "".join(offset_string)
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists("token.json"):
                        os.remove("token.json")
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port = 0)

                with open("token.json", "w") as token:
                    token.write(creds.to_json())

        try:
            service = build("calendar", "v3", credentials = creds)
            now = dt.datetime.now().isoformat() + "Z"
            event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()

            events = event_result.get("items", [])

            if not events:
                print("No upcoming events found!")
            else:
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    print(start, event["summary"])

            # event = {
            #     "summary": "My Python Event",
            #     "location": "Somewhere Online",
            #     "description": "",
            #     "colorId": 6,
            #     "start": {
            #         "dateTime": "2024-02-11T09:00:00" + timeZone,
            #     },

            #     "end": {
            #         "dateTime": "2024-02-11T17:00:00" + timeZone,
            #     },
            # }
            # time.wait(5)

            # event = service.events().insert(calendarId = "primary", body = event).execute()
            # print(f"Event Created {event.get('htmlLink')}")
            print(schedule)
            for query in schedule:
                print(query)
            #     time.wait(5)
                taskSummary = query['task']
                taskStart = query['start_time']
                taskEnd = query['end_time']
                
            #     # Add time zone offset to date-time strings (assuming they're in ET
                
                event = {
                    "summary": taskSummary,
                    "location": "",
                    "description": "",
                    "colorId": 6,
                    "start": {
                        "dateTime": taskStart + timeZone,
                        # "timeZone": "Eastern Time"
                    },

                    "end": {
                        "dateTime": taskEnd + timeZone,
                        # "timeZone": "Eastern Time"
                    },
                    # "recurrence": [
                    #     "RRULE: FREQ=DAILY;COUNT=3"
                    # ],
                    # "attendees": [
                    #     {"email": "social@neuralnine.com"},
                    #     {"email": "pedropa828@gmail.com"},
                    # ]
                }


                event = service.events().insert(calendarId = "primary", body = event).execute()
                print(f"Event Created {event.get('htmlLink')}")
            

        except HttpError as error:
            print("An error occurred:", error)
        response = {
            "content": content
        }
        #print(content)
       # successString = "Tasks Successfully Added to Calendar"
        return jsonify({"message": "Tasks Successfully Added to Calendar"})    
    else:
        return render_template("taskschedule.html")
    
@app.route("/education")
def education():
    return render_template("education.html")

if __name__ == "__main__":
    app.run(debug=True)