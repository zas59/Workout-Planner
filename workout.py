import random
import os
from urllib.parse import urlparse, urljoin
import requests
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def find_workouts():
    return render_template('search_workout.html')

@app.route('/handle_workout_search', methods=['GET', 'POST'])
def handle_workout_search():
    form_data = request.form
    API_URL = 'https://exercises-by-api-ninjas.p.rapidapi.com/v1/exercises'
    api_key = os.getenv('X_API_KEY')
    headers = {
	"X-RapidAPI-Key": api_key,
	"X-RapidAPI-Host": "exercises-by-api-ninjas.p.rapidapi.com"
    }
    querystring = {"muscle": form_data['targetArea'], "difficulty": form_data['difficulty']}
    response = requests.get(
        API_URL,
        headers=headers,
        params=querystring
    )
    json_data = response.json()
    workouts_obj = json_data
    return render_template('display_options.html', results = workouts_obj)

@app.route('/handle_workout_selection', methods=['GET', 'POST'])
def handle_workout_selection():
    form_data = request.form
    API_URL = 'https://exercises-by-api-ninjas.p.rapidapi.com/v1/exercises'
    api_key = os.getenv('X_API_KEY')
    headers = {
	"X-RapidAPI-Key": api_key,
	"X-RapidAPI-Host": "exercises-by-api-ninjas.p.rapidapi.com"
    }
    querystring = {'name': form_data['chosenWorkout']}
    response = requests.get(
        API_URL,
        headers=headers,
        params=querystring
    )
    json_data = response.json()
    workout_obj = json_data
    chosenWorkout = ''
    for workout in workout_obj:
        if str(form_data['chosenWorkout']) == str(workout['name']):
            chosenWorkout = workout['name']
            return render_template('show_chosen_workout.html', workout = chosenWorkout)
app.run()