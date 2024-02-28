from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, UsersInfo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.io'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables before the first request
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Collect and validate form data, then store in database
        user = UsersInfo(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            phone_number=request.form['phone_number'],
            state=request.form['state']
        )
        db.session.add(user)
        db.session.commit()
        flash('Signup successful!')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Implement login functionality
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Protected route for logged-in users
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
