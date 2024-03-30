import os
import sqlite3
from os import urandom
from dotenv import load_dotenv
import os.path
import json
import PyPDF2
import requests

# Third-Party Imports
from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g, session
from datetime import datetime, timezone
import datetime as dt
from authlib.integrations.flask_client import OAuth

import google.generativeai as genai
from google.auth import load_credentials_from_file
from google.oauth2 import credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.generativeai import generative_models
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
SCOPES = ['https://www.googleapis.com/auth/calendar']

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

try:
    api_key = os.getenv("GENAI_API_KEY")
    if api_key:
        genai_client = generative_models.GenerativeModelsServiceClient(api_key=api_key)
    else:
        print("GENAI_API_KEY environment variable is not set.")
except Exception as e:
    print("Error initializing GenAI client:", e)

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
def talktoAI():
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

@app.route("/upload")
def index():
    return render_template("upload.html")
@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    if "pdf_file" not in request.files:
        return "No file part"

    pdf_file = request.files["pdf_file"]

    if pdf_file.filename == "":
        return "No selected file"

    if pdf_file:
        pdf_text = extract_text_from_pdf(pdf_file)
        query = "As a chatbot, your goal is to summarize the the following text from a pdf in a format that easiliy digestible for a college student. Try to keep it as concise as possible: " + pdf_text
        model = genai.GenerativeModel('models/gemini-pro')
        result = model.generate_content(query)
        formatted_message = ""
        lines = result.text.split("\n")

        for line in lines:
            bold_text = ""
            while "**" in line:
                start_index = line.index("**")
                end_index = line.index("**", start_index + 2)
                bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
                line = line[:start_index] + bold_text + line[end_index + 2:]
            formatted_message += line + "<br>"
        print(formatted_message)
        print(result.text)
        return formatted_message

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page_num in range(num_pages):
        text += pdf_reader.pages[page_num].extract_text()
    return text

if __name__ == "__main__":
    app.run(debug=True)