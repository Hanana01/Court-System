from flask_mail import Mail, Message
from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer

# Import 'mail' from the main app


def get_serializer():
    # Ensure we are within the app context
    return URLSafeTimedSerializer(current_app.secret_key)

# Updated send_verification_email function
def send_verification_email(email, username):
    from app import mail
    serializer = get_serializer()
    token = serializer.dumps(email, salt='email-verification-salt')
    verify_url = url_for('verify_email', token=token, _external=True)
    msg = Message('Verify Your Email', sender='jasar9866@gmail.com', recipients=[email])
    msg.body = f'Hi {username}, please verify your email by clicking the link: {verify_url}'
    mail.send(msg)
