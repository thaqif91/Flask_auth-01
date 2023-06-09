import sqlalchemy.exc
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

############## login manager setup #################
# Initialize the Flask-Login extension
login_manger = LoginManager()
login_manger.init_app(app)


# Define a user_loader function that retrieves a User object from the user ID
@login_manger.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


######################################################

# Flask secret key
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
# Connect to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    # def __init__(self, id):
    #     self.id=id


# Line below only required once, when creating DB.
# db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # Get input data from html input form get by name
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        hash_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        new_register = User(
            email=email,
            password=hash_password,
            name=name
        )
        try:
            db.session.add(new_register)
            db.session.commit()
            # Log in and authenticate user after adding details to database.
            login_user(new_register)
            return redirect(url_for("secrets"))
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback() #buat video tiktok
            flash('The email already use, Please use another email')
    return render_template("register.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        print(password)

        # find user by email entered
        user = User.query.filter_by(email=email).first()
        if not user :
            flash('The email does not exits, Please try again')
        elif not check_password_hash(user.password, password): # check stored password hash against enter password hash
            flash('The password is incorrect, please try again')
        else:
            # flash('You were successfully logged in')
            login_user(user)
            return redirect(url_for('secrets'))
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name, logged_in=True)  # current user got from flask login library


@app.route('/logout')
def logout():
    pass


# Download selected file
@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory("static/files", filename)

# if __name__ == "__main__":
#     app.run(debug=True)
