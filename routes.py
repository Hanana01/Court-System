from flask import render_template, request, redirect, Blueprint, flash
from db_operations import cursor

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def index():
    return render_template('index.html')

@routes_bp.route('/login')
def login():
    return render_template('login.html')

@routes_bp.route('/register')
def register():
    return render_template('registration.html')

@routes_bp.route('/users')
def users():
    # Retrieve all registered users from the database
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print(users)  
    return render_template('users.html', users=users)

@routes_bp.route('/contact')
def contact():
    return render_template('contact.html')


@routes_bp.route('/IntroPage')
def landpage():
    return render_template('landingPage.html')

@routes_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')






