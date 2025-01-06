
from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegistrationForm

from flask_login import current_user, login_user, logout_user, login_required

import sqlalchemy as sa
from app import db
from app.models import User

from urllib.parse import urlsplit

import base64
from io import BytesIO

import seaborn as sns
import matplotlib.pyplot as plt
import os
import pandas as pd


@app.route('/')
@app.route('/index')
# @login_required
def index():
    # user = {'username': 'Aoife'}
    posts = [
        {
            'author': {'username': 'Aoife'},
            'body': 'John Hodnett is the woat!'
        },
        {
            'author': {'username': 'Ben'},
            'body': 'Leo out!'
        }
    ]
    return render_template('index.html', title='Home Page', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next') # get the url that the user was trying to navigate to
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/league_projections', methods=['GET'])
def league_projections():
    # load in data from csv

    return render_template('league_projections.html', title='Projections Page')


@app.route('/league_projections_output', methods=['GET', 'POST'])
def league_projections_output():
    league = request.form.get('league')
    n_simulations = request.form.get('n_simulations')



    df = pd.read_csv('app/urc_predicted_finish.csv')
    df.fillna(0, inplace=True)

    # https://stackoverflow.com/questions/52644035/how-to-show-a-pandas-dataframe-into-a-existing-flask-html-table
 
    return render_template("league_projections_output.html", 
                           column_names=df.columns.values, 
                           row_data=list(df.values.tolist()),
                            link_column="Patient ID", zip=zip
                           )