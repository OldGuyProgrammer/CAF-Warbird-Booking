# Flask Email
# Jim Olivi
# 2023

from flask import Flask
from flask_mail import Mail, Message
from globals import signals as sigs, globals as gl
import os

# TODO App speciific password needed for gmail

class FlaskMail:
    def __init__(self, app):
        self.app = app
        app.config['MAIL_SERVER']='smtp.gmail.com'
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = 'jimolivi@gmail.com'
        password = os.getenv("GMAIL_APP_PWD")
        app.config['MAIL_PASSWORD'] = password
        # TLS uses MAIL_PORT = 587
        # Use TLS or SSL but not both
        app.config['MAIL_USE_TLS'] = False
        # SSL uses MAIL_PORT = 465
        app.config['MAIL_USE_SSL'] = True
        self.mail = Mail(self.app)

    def send_message(self, subject, recipient, msg_text):
        with self.app.app_context():
            try:
                msg = Message(subject, sender='jimolivi@gmail.com', recipients=[recipient])
                msg.body = msg_text
                self.mail.send(msg)
            except Exception as e:
                errmsg = f'Mail Send failed {e}'
                print (errmsg)
                # If failure, return failure code and a message
                return [sigs.failure, errmsg]
            else:
                # If success, return the key of the new record.
                return [sigs.success, gl.MSG_MESSAGE_SENT]


