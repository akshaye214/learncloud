from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User, Course

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
admin = Blueprint('admin', __name__)

# --- Main Routes ---
@main.route('/')
def home():
    courses = Course.query.all()
    return render_template('home.html', courses=courses)

@main.route('/course/<int:id>')
def course_detail(id):
    course = Course.query.get_or_404(id)
    return render_template('course_detail.html', course=course)

# --- Auth Routes ---
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# --- Admin Routes ---
@admin.route('/admin')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.home'))
    users = User.query.all()
    courses = Course.query.all()
    return render_template('admin.html', users=users, courses=courses)

@admin.route('/admin/add-course', methods=['GET', 'POST'])
@login_required
def add_course():
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        course = Course(
            title=request.form['title'],
            description=request.form['description'],
            instructor=request.form['instructor']
        )
        db.session.add(course)
        db.session.commit()
        flash('Course added!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('add_course.html')

@admin.route('/admin/delete-course/<int:id>')
@login_required
def delete_course(id):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted!', 'success')
    return redirect(url_for('admin.dashboard'))