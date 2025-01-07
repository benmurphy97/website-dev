from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
# from flask_pymongo import PyMongo


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

#  add mongo url to flask config, so that flask_pymongo can use it to make connection
# app.config['MONGO_URI'] = os.environ.get('nebflix')
# app.config['MONGO_URI'] = "mongodb://localhost:27017/nebflix"
# mongo = PyMongo(app)

from app import routes, models
