from flask import Blueprint, render_template, request, flash, jsonify
from db_operations import cursor, db

registration_tasks_bp = Blueprint('registration_tasks', __name__)

@registration_tasks_bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['uname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        gender = request.form['gender']  # Fetch values from form data
        
        # Insert data into database
        cursor.execute("INSERT INTO users (name, username, email, phone, password, gender) VALUES (%s, %s, %s, %s, %s, %s)", 
                        (name, username, email, phone, password, gender))
        db.commit()
        
        # Flash success message
        flash('You have successfully registered your account!', 'success')
        
        return jsonify({'status': 'success'})

    return render_template('registration.html')