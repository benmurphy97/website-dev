
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

from data_scraping.match_scraper import get_base_url, get_links_df, scrape_matches_from_links
from app.data_writer import write_to_postgres_table

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

    df[df.select_dtypes(include=['number']).columns] *= 100

    # https://stackoverflow.com/questions/52644035/how-to-show-a-pandas-dataframe-into-a-existing-flask-html-table
 
    row_data=list(round(df,2).values.tolist())


    return render_template("league_projections_output.html", 
                           column_names=df.columns.values, 
                           row_data=row_data,
                           link_column="Patient ID", 
                           zip=zip
                           )




#background process happening without any refreshing
@app.route('/scrape_match_data', methods=['GET', 'POST'])
def scrape_match_data():

    # get values passed from form
    league = request.form.get('league')
    season = request.form.get('season')
    print (f"Scraping running for {league} season: {season}")

    # base_url = get_base_url(league, season)
    # print(base_url)

    # links_df, scores = get_links_df(base_url)
    # print(links_df.head())

    # df = scrape_matches_from_links(links_df, scores)
    # print(df.head())

    # df.to_csv('matches.csv', index=False)
    print("loading data from csv")
    df = pd.read_csv('matches.csv')

    print(df.dtypes)

    df['league'] = league
    df['season'] = season

    df['match_date_dt'] = pd.to_datetime(df['match_date'])
    df['match_date_str'] = df['match_date_dt'].dt.strftime("%Y-%m-%d")

    import re
    df['home_score'] = df['match_result'].apply(lambda x: re.findall(r'[\d]+', x)[0]).astype(int)
    df['away_score'] = df['match_result'].apply(lambda x: re.findall(r'[\d]+', x)[1]).astype(int)


    def match_outcome(h,a):
        if h > a: # home win
            if (h - a) > 7:
                return 2
            else:
                return 1 # away team gets bonus pt
            
        elif h < a: # away win
            if (a - h) > 7:
                return -2
            else:
                return -1 # home team gets bonus pt
        else:
            return 0
    
    df['long_outcome'] = df.apply(lambda x: match_outcome(x.home_score, x.away_score), axis=1)

    import datetime
    df.loc[df['match_date_dt'] >= datetime.datetime.today(), 'home_score'] = 0
    df.loc[df['match_date_dt'] >= datetime.datetime.today(), 'away_score'] = 0

    cols_to_write = ['match_date_str', 'season', 'league', 'home_team', 'away_team', 'link',
                     
                     'match_result', 'home_score', 'away_score', 'long_outcome',
                     
                     'home_n_tries', 'away_n_tries',
                     'home_n_conversions', 'away_n_conversions',
                     'home_n_pen_kicks', 'away_n_pen_kicks',
                     'home_n_pen_tries', 'away_n_pen_tries'
                     ]
    

    df.fillna(0, inplace=True)

    print(df[cols_to_write].tail())


    write_to_postgres_table(df[cols_to_write], table='matches_raw')


    return render_template('match_data_scraping.html', title='Match Scraping')


@app.route('/match_scraping', methods=['GET'])
def match_scraping():

    # get things from database
    # most recent date of match in database


    return render_template('match_data_scraping.html', title='Match Scraping')
