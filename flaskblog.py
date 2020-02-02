from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['SECRET_KEY'] = '3f962c15cca6ee00866c8aa698953946'
app.config['MONGO_DBNAME'] = 'flaskblog'
app.config["MONGO_URI"] = "mongodb+srv://guest:stropczyk@database-pjbt9.mongodb.net/test?retryWrites=true&w=majority"

mongo = PyMongo(app)

posts2 = [
    {'author': 'Karol Stropek',
     'title': 'Blog Post 1',
     'content': 'First post content',
     'date_posted': 'January 20, 2020'
    },
    {'author': 'Jane Doe',
     'title': 'Blog Post 2',
     'content': 'Second post content',
     'date_posted': 'January 21, 2020'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts2)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        if mongo.db.users.find_one({"username": form.username.data}) == 'null':
            mongo.db.users.insert({
                "username": form.username.data,
                "email": form.email.data,
                "password": form.password.data
            }
            )
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)

