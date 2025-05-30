#﻿# Test_Management
# Online Examination System

# Project Overview
This is a web-based *Online Examination System* built using *Flask* and *PostgreSQL*. The system allows users to register, log in, and take online tests. Admins can manage users, test types, and test questions, as well as allocate tests to students.

# Features
- User Registration & Authentication
  - OTP-based email verification
  - Profile picture upload
  - Secure password storage with hashing
- Dashboard
  - User statistics
  - Test performance tracking
- User Management
  - List, search, edit, delete users
  - Add new users manually
- Test Management
  - Test Type creation and management
  - Test Master module for managing questions
  - Question image upload
- Test Allocation
  - Assign tests to specific users
  - View allocated tests
- Examination Process
  - Fetch questions for a selected test
  - Submit answers and calculate score
  - Automatic pass/fail determination
- Reports
  - View test attempts and results
  - Overall statistics of passed/failed students
- User Session Management
  - Secure login/logout
  - user authentication

# Technologies Used
- Backend: Flask (Python), Flask-Mail, SQLAlchemy
- Frontend: HTML, CSS, Bootstrap
- Database: PostgreSQL
- Security: Password Hashing, Secure Sessions

# Installation Guide

# Prerequisites
- Python (>=3.8)
- PostgreSQL
- Virtual Environment (recommended)

# Setup Instructions
1. Download files from Zip folder and add it to your folder

2. Create and activate a virtual environment:
   python -m venv venv
   On Windows: venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Set up the database:
   - Create a PostgreSQL database
   - Update `config.py` with your database and Mail credentials 
   - Run database migrations:
     flask db init
     flask db migrate -m "Initial migration"
     flask db upgrade

5. Run the application:

   flask run
   The app will be accessible at `http://127.0.0.1:5000/`.

# Configuration
Update the `config.py` file with your PostgreSQL and email SMTP settings:

class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/examdb'
    MAIL_SERVER = 'smtp.yourmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@example.com'
    MAIL_PASSWORD = 'your-email-password'


# Folder Structure
/online-exam-system
│── /static          # Static assets (CSS, JS, images)
│── /templates       # HTML templates
│── config.py        # Application configuration
│── extensions.py    # Flask extensions setup
│── models.py        # Database models
│── app.py           # Main application file
│── requirements.txt # Dependencies list
│── README.md        # Documentation


# Future Enhancements
- Role-based access control (Admin, Student, Teacher)
- Timer-based test attempts
- Detailed test analytics
- Multi-language support
