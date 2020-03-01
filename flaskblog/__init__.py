from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
# app = Blueprint('flaskblog', __name__)

app.config['SECRET_KEY'] = '3f962c15cca6ee00866c8aa698953946'
app.config["MONGO_URI"] = "mongodb+srv://guest:stropczyk@database-pjbt9.mongodb.net/flaskblog?retryWrites=true&w=majority"

db = PyMongo(app)
b_crypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskblog import routes
