from os import urandom
import random
from dotenv import load_dotenv
import os.path
import PyPDF2
import pymongo
import requests
from flask import send_file
from werkzeug.utils import secure_filename


# Third-Party Imports
from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g, session
from datetime import datetime, timezone
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

SCOPES = ['https://www.googleapis.com/auth/calendar',  'https://www.googleapis.com/auth/presentations']

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

def create_presentation():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("slides", "v1", credentials=creds)

    presentation = service.presentations().create(
        body={'title': 'My Presentation'}).execute()
    presentation_id = presentation.get('presentationId')

    # Define the slides content
    slides_content = [
        {'title': 'My Name', 'content': 'Your Name Here'},
        {'title': 'Where I Am From', 'content': 'Your Location Here'}
    ]

    # Create slides
    requests = []
    for slide_content in slides_content:
        slide = service.presentations().pages().batchUpdate(
            presentationId=presentation_id,
            body={'title': slide_content['title'], 'elementProperties': {'pageObjectId': ''}},
        ).execute()

        # Insert text into slides
        requests.append({
            'insertText': {
                'objectId': slide['objectId'],
                'text': slide_content['content'],
            }
        })

    # Execute batch requests to insert text
    batch_update_body = {
        'requests': requests
    }
    service.presentations().batchUpdate(
        presentationId=presentation_id, body=batch_update_body).execute()

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

            presentation_id = create_presentation()


            pdf_path = "uploaded.pdf"
            pdf_file.save(pdf_path)
            pdf_file.save(filepath)
            session['current_filename'] = filename  # Save the current filename in the session

            # Set the current_pdf variable to True to indicate that a PDF has been uploaded
            session['current_pdf'] = True

            return render_template("upload.html", formatted_message=formatted_message, current_pdf=True)

    return render_template("upload.html")

@app.route("/show_pdf")
def show_pdf():
    if 'current_filename' in session:
        filename = session['current_filename']
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return "No PDF uploaded"

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page_num in range(num_pages):
        text += pdf_reader.pages[page_num].extract_text()
    return text

@app.route("/dashboard/")
def dashboard():
    card_data = [
        {"title": "Card Title {}".format(i), 
         "text": "Some example text for card {}".format(i),
         "image": "https://picsum.photos/id/{}/350/150".format(random.randint(1, 100))
        } for i in range(5)  # Generate 5 cards
    ]
    return render_template('dashboard.html', cards=card_data)

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

    Task Description: Meeting with client
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

            print(schedule)
            for query in schedule:
                print(query)
                taskSummary = query['task'].replace('"', '')
                print(taskSummary)
                taskStart = query['start_time']
                taskEnd = query['end_time']
                
                
                event = {
                    "summary": taskSummary,
                    "location": "",
                    "description": "",
                    "colorId": 6,
                    "start": {
                        "dateTime": taskStart + timeZone,
                    },

                    "end": {
                        "dateTime": taskEnd + timeZone,
                    },
                }


                event = service.events().insert(calendarId = "primary", body = event).execute()
                print(f"Event Created {event.get('htmlLink')}")
            

        except HttpError as error:
            print("An error occurred:", error)
        response = {
            "content": content
        }
        return jsonify({"message": "Tasks Successfully Added to Calendar"})    
    else:
        return render_template("taskschedule.html")
    
@app.route("/cal")
def cal():
    return render_template("cal.html")


if __name__ == "__main__":
    app.run(debug=True)