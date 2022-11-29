'''Workout Planning App by Zach and Jake. Name TBD, TXST SWE, EIR Laith Hasanian.'''
import os
from datetime import date
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
workout = {}
workout['today'] = ''

app = Flask(__name__)
app.secret_key = 'super_secret_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL')
db = SQLAlchemy(app)

class People(UserMixin, db.Model):
    '''Table of Users'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)

    def __repr__(self) -> str:
        return self.username

class Workouts(db.Model):
    '''Table listing the target muscle(s) for a user in a workout session, and date.'''
    session_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    targets = db.Column(db.String(200))
    date = db.Column(db.String(100))

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    '''User Loader for flask_login'''
    return People.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def find_workouts():
    '''Function for Landing Page'''
    return render_template('search_workout.html', login_link=url_for('login'),
    logout_link=url_for('logout'))

@app.route('/login')
def login():
    '''Login form page'''
    return render_template('login.html', signup_link=url_for('signup'))

@app.route('/signup')
def signup():
    '''Display signup form'''
    return render_template('signup.html', login_link = url_for('login'))

@app.route('/logout')
@login_required
def logout():
    '''Display logout option screen'''
    logout_user()
    return render_template('logout.html')

@app.route('/handle_login', methods=['POST'])
def handle_login():
    '''Logs user in'''
    valid_users = []
    form_data = request.form
    print(f'FORM DATA: {form_data}')
    given_username = form_data['enter_username']
    for person in People.query.all():
        valid_users.append(person.username)
    if given_username in valid_users:
        this_user = People.query.filter_by(username=given_username).first()
        login_user(this_user)
        session['user'] = given_username
        return redirect(url_for('find_workouts'))
    else:
        flash('Error: This username is does not exist')
        return redirect(url_for('login'))

@app.route('/handle_signup', methods=['POST'])
def handle_signup():
    '''Allows a user to create a new account with a given username'''
    form_data = request.form
    given_username = form_data['username']
    existing = People.query.filter_by(username=given_username).first()
    if existing:
        flash('Error: This username already exists. User was not added.')
        return redirect(url_for('login'))
    else:
        new_user = People(id=int(len(People.query.all())), username=given_username)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Created new user with username {repr(new_user)}')
        return redirect(url_for('login'))

@app.route('/handle_workout_search', methods=['GET', 'POST'])
def handle_workout_search():
    '''Search for and render workout suggestions.'''
    form_data = request.form
    api_url = 'https://exercises-by-api-ninjas.p.rapidapi.com/v1/exercises'
    api_key = os.getenv('X_API_KEY')
    headers = {
	"X-RapidAPI-Key": api_key,
	"X-RapidAPI-Host": "exercises-by-api-ninjas.p.rapidapi.com"
    }
    querystring = {"muscle": form_data['targetArea'], "difficulty": form_data['difficulty']}
    response = requests.get(
        api_url,
        headers=headers,
        params=querystring
    )
    json_data = response.json()
    workouts_obj = json_data
    return render_template('display_options.html', results = workouts_obj,
    target_area=form_data['targetArea'])

@app.route('/handle_workout_submission', methods=['GET', 'POST'])
@login_required
def handle_workout_submission():
    '''Handle a users report of their workout'''
    form_data = request.form
    num_sets = form_data['sets']
    target_area = form_data['target_area']
    todays_workout = workout['today']
    workout['today'] = f'{target_area} sets: {num_sets}. {todays_workout}'
    flash(f'Added {target_area} to this workout.')
    return render_template('continue_end.html')

@app.route('/continue_response', methods=['POST'])
@login_required
def continue_response():
    '''The user opted to continue the workout session'''
    return render_template('multitarget_workout.html')

@app.route('/end_workout', methods=['POST'])
@login_required
def end_workout():
    '''End the users workout session, store to database'''
    today = date.today()
    formatted_date = today.strftime("%B %d, %Y")
    this_workout = Workouts(session_id=int(len(Workouts.query.all())),
    username=session['user'], targets=workout['today'], date=formatted_date)
    db.session.add(this_workout)
    db.session.commit()
    logout_user()
    flash(f'Saved workout from {formatted_date}')
    return render_template('logout.html')

app.run()
