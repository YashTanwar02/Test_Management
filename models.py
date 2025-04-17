from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db  # Import db from extensions.py

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    profile_picture = db.Column(db.String(255), default='default.png')  # Default profile picture
    otp = db.Column(db.String(6))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tests = db.relationship('Test', backref='creator', lazy=True, cascade="all, delete")
    attempts = db.relationship('Attempt', backref='user', lazy=True, cascade="all, delete")

    def set_password(self, password):
        """Hash and store the password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    test_type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attempts = db.relationship('Attempt', backref='test', lazy=True, cascade="all, delete")

class Attempt(db.Model):
    __tablename__ = 'attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class TestType(db.Model):
    __tablename__ = 'test_types'
    id = db.Column(db.Integer, primary_key=True)
    test_type = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TestMaster(db.Model):
    __tablename__ = 'test_master'
    id = db.Column(db.Integer, primary_key=True)
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_types.id'), nullable=False)  # Fixed FK reference
    question = db.Column(db.Text, nullable=False)
    question_image = db.Column(db.String(255), nullable=True)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    creator = db.relationship('User', backref=db.backref('test_master', lazy=True))
    test_type = db.relationship('TestType', backref=db.backref('test_master', lazy=True))

class AllocatedTest(db.Model):
    __tablename__ = 'allocated_tests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_types.id', ondelete="CASCADE"), nullable=False)  # Fixed FK reference
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='allocated_tests')
    test_type = db.relationship('TestType', backref='allocated_tests')
    
class ExamAttempt(db.Model):
    __tablename__ = 'exam_attempts'  # Explicit table name

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_types.id',ondelete="CASCADE"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'Passed' or 'Failed'
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='exam_attempts')
    test_type = db.relationship('TestType', backref='exam_attempts')

