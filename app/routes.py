from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Aoife'}
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
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form)
