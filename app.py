import os  
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename  
import random
from config import Config  
from extensions import db, migrate  
from models import User, Test, Attempt, TestType, TestMaster, AllocatedTest, ExamAttempt  
from sqlalchemy import text 

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Load configurations
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)

# File upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create directory for uploads if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize Flask-Mail
mail = Mail(app)

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to send OTP
def send_otp(email, otp):
    msg = Message('Email Verification OTP', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Your OTP for email verification is {otp}'
    mail.send(msg)

@app.route('/')
def home():
    return redirect(url_for('register'))

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form['phone']
        file = request.files['profile_picture']

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('login'))

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        otp = str(random.randint(100000, 999999))

        # Handle profile picture upload
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            filename = 'default.png'  # Default profile picture

        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            profile_picture=filename,
            otp=otp,
            is_verified=False
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        send_otp(email, otp)
        flash('Registration successful! Please login and verify your email.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Verify OTP
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('register'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        if user.otp == entered_otp:
            user.is_verified = True
            db.session.commit()
            session['user_id'] = user.id
            flash("Verification successful! Welcome to your dashboard.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect(url_for('verify', email=email))

    return render_template('verify.html', email=email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_verified:
                return redirect(url_for('verify', email=email))
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('login'))

    # Dashboard statistics
    total_students = User.query.count()
    new_students = User.query.filter(User.is_verified == True).count()
    test_types = test_types = TestType.query.count()
    total_attempts = ExamAttempt.query.count()
    passed_attempts = ExamAttempt.query.filter_by(status='Passed').count()
    failed_attempts = ExamAttempt.query.filter_by(status='Failed').count()

    return render_template('dashboard.html', 
        user=user,
        total_students=total_students, 
        new_students=new_students,
        test_types=test_types,
        total_attempts=total_attempts,
        passed_attempts=passed_attempts,
        failed_attempts=failed_attempts
    )
    
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Users List & Search
@app.route('/users', methods=['GET', 'POST'])
def users():
    search_query = request.form.get('search', '')  # Get search input
    if search_query:
        users = User.query.filter(User.full_name.ilike(f"%{search_query}%")).all()
    else:
        users = User.query.all()
    
    return render_template('users.html', users=users)

# Edit User
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        user.phone = request.form['phone']
        db.session.commit()
        flash("User updated successfully!", "success")
        return redirect(url_for('users'))

    return render_template('edit_user.html', user=user)

# Delete User
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "danger")
    return redirect(url_for('users'))

# Add User
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form.get("password")
        password_hash = generate_password_hash(password) 

        
        new_user = User(full_name=full_name, email=email, phone=phone,password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        
        flash("User added successfully!", "success")
        return redirect(url_for('users'))  # Redirect to users list
    
    return render_template('add_user.html')

#Test Type Page
@app.route('/test-type', methods=['GET', 'POST'])
def test_type():
    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()  # Get search input

        if search_query:
            test_types = TestType.query.filter(TestType.test_type.ilike(f'%{search_query}%')).all()
        else:
            test_types = TestType.query.all()
    else:
        test_types = TestType.query.all()

    return render_template('test_type.html', test_types=test_types)


@app.route('/add-test-type', methods=['GET', 'POST'])
def add_test_type():
    if request.method == 'POST':
        test_type = request.form.get('test_type')
        language = request.form.get('language')

        if not test_type or not language:
            flash("All fields are required!", "error")
            return redirect(url_for('add_test_type'))

        new_test = TestType(test_type=test_type, language=language)
        db.session.add(new_test)
        db.session.commit()
        flash("Test Type added successfully!", "success")

        return redirect(url_for('test_type'))

    return render_template('add_test_type.html')

@app.route('/delete-test-type/<int:id>', methods=['GET'])
def delete_test_type(id):
    try:
        # Delete all related exam_attempts records
        ExamAttempt.query.filter_by(test_type_id=id).delete()
        
        # Now delete the test type
        TestType.query.filter_by(id=id).delete()
        
        db.session.commit()
        flash("Test Type deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting Test Type: {str(e)}", "danger")
    return redirect(url_for('test_type'))


# TEST MASTER

UPLOAD_FOLDER = 'static/uploads/questions'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/test-master', methods=['GET', 'POST'])
def test_master():
    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()
        test_master = TestMaster.query.filter(TestMaster.question.ilike(f'%{search_query}%')).all()
    else:
        test_master = TestMaster.query.all()
    return render_template('test_master.html', test_master=test_master)

@app.route('/add-test-master', methods=['GET', 'POST'])
def add_test_master():
    if request.method == 'POST':
        test_type_id = request.form.get('test_type')  # Get test type ID from form
        
        if not test_type_id or not test_type_id.isdigit():
            flash("Invalid Test Type selected", "error")
            return redirect(url_for('add_test_master'))
        
        test_type_id = int(test_type_id)  # Convert to integer

        question = request.form.get('question')
        question_image = request.files.get('question_image')
        option_a = request.form.get('option_a')
        option_b = request.form.get('option_b')
        option_c = request.form.get('option_c')
        option_d = request.form.get('option_d')
        correct_option = request.form.get('correct_option')
        created_by = session.get('user_id')

        if question_image and question_image.filename:
            filename = secure_filename(question_image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            question_image.save(image_path)
        else:
            filename = None

        new_test_master = TestMaster(
            test_type_id=test_type_id,  # Assign the integer ID, not an object or string
            question=question,
            question_image=filename,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            created_by=created_by
        )

        db.session.add(new_test_master)
        db.session.commit()
        flash('Test question added successfully!', 'success')
        return redirect(url_for('test_master'))

    test_types = TestType.query.all()
    return render_template('add_test_master.html', test_types=test_types)


@app.route('/delete-test-master/<int:test_id>', methods=['GET'])
def delete_test_master(test_id):
    test_entry = TestMaster.query.get_or_404(test_id)
    db.session.delete(test_entry)
    db.session.commit()
    flash('Test question deleted successfully!', 'success')
    return redirect(url_for('test_master'))


@app.route('/allocate_test', methods=['GET', 'POST'])
def allocate_test():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        test_type_id = request.form.get('test_type_id')
        
        if not user_id or not test_type_id:
            flash('Please select both user and test type.', 'error')
            return redirect(url_for('allocate_test'))
        
        allocation = AllocatedTest(user_id=user_id, test_type_id=test_type_id)
        db.session.add(allocation)
        db.session.commit()
        flash('Test allocated successfully!', 'success')
        return redirect(url_for('allocate_test'))

    users = User.query.all()
    test_types = TestType.query.all()
    allocated_tests = AllocatedTest.query.order_by(AllocatedTest.assigned_at.desc()).all()
    
    return render_template('allocate_test.html', users=users, test_types=test_types, allocated_tests=allocated_tests)


@app.route('/delete_allocated_test/<int:allocation_id>', methods=['GET'])
def delete_allocated_test(allocation_id):
    allocation = AllocatedTest.query.get_or_404(allocation_id)
    db.session.delete(allocation)
    db.session.commit()
    flash("Allocated test deleted successfully!", "success")
    return redirect(url_for('allocate_test'))


@app.route('/user_test')
def user_test():
    test_types = TestType.query.all()
    return render_template('user_test.html', test_types=test_types)


@app.route('/get_questions/<int:test_type_id>', methods=['GET'])
def get_questions(test_type_id):
    from flask import jsonify
    from models import TestMaster  # Ensure this is imported
    
    questions = TestMaster.query.filter_by(test_type_id=test_type_id).all()
    
    if not questions:
        return jsonify({"questions": []})
    
    question_list = []
    for q in questions:
        question_list.append({
            "id": q.id,
            "question": q.question,
            "question_image": q.question_image if q.question_image else "",
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "correct_option": q.correct_option
        })
    
    return jsonify({"questions": question_list})

@app.route('/submit_test', methods=['POST'])
def submit_test():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.json
    test_type = data.get('test_type')
    score = data.get('score')
    total_questions = data.get('total_questions')

    # Determine pass/fail 
    passing_score = total_questions 
    status = "Passed" if score >= passing_score else "Failed"

    # Save attempt in the database
    new_attempt = ExamAttempt(user_id=user_id, test_type_id=test_type, score=score, total_questions=total_questions, status=status)
    db.session.add(new_attempt)
    db.session.commit()

    return jsonify({'message': 'Test result saved successfully'})


@app.route('/reports')
def reports():
    exam_attempts = ExamAttempt.query.join(User).join(TestType).all()
    
    total_students = User.query.count()
    pass_count = ExamAttempt.query.filter_by(status='Passed').count()
    fail_count = ExamAttempt.query.filter_by(status='Failed').count()
    
    return render_template('reports.html', 
                           exam_attempts=exam_attempts, 
                           total_students=total_students, 
                           pass_count=pass_count, 
                           fail_count=fail_count)


# Database initialization
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)