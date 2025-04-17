import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_random_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:12345@localhost/PT'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # Mail Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'yash.tanwar3008@gmail.com'
    MAIL_PASSWORD = 'boqs tbqw ooyl wuvi'
