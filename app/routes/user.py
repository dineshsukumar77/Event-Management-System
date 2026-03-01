from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from bson import ObjectId
from datetime import datetime
from functools import wraps

user_bp = Blueprint('user', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] not in ['Admin', 'SuperAdmin']:
            flash('Admin access required.', 'danger')
            return redirect(url_for('user.user_login_page'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/registerForm', methods=['POST'])
def user_register():
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    contactno = request.form.get('contactno')
    role = request.form.get('role', 'User')
    gender = request.form.get('gender')
    address = request.form.get('address')
    if password != confirm_password:
        flash('Password and Confirm Password do not match', 'danger')
        return render_template('UserRegisteration.html')
    # Unique email check in Mongo
    if current_app.mongo_db.users.find_one({'email': email}):
        flash('User Email Already Taken', 'danger')
        return render_template('UserRegisteration.html')
    doc = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'password': password,
        'confirm_password': confirm_password,
        'contactno': contactno,
        'role': role,
        'gender': gender,
        'address': address
    }
    res = current_app.mongo_db.users.insert_one(doc)
    # Stub: send SMS/email here
    flash('Registration successful! Please sign in.', 'success')
    return redirect(url_for('user.user_login_page'))

@user_bp.route('/signin', methods=['GET'])
def user_login_page():
    return render_template('Login.html')

@user_bp.route('/login-validation', methods=['POST'])
def user_login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = current_app.mongo_db.users.find_one({'email': email})
    if user and user.get('password') == password:
        session['user_id'] = str(user.get('_id'))
        session['user_role'] = user.get('role')
        session['user_firstname'] = user.get('first_name')
        session['user_lastname'] = user.get('last_name')
        session['user_email'] = user.get('email')
        session['user_phone'] = user.get('contactno')
        session['user_address'] = user.get('address')
        session['user_gender'] = user.get('gender')
        role = user.get('role')
        if role == 'Admin':
            return redirect('/adminhome')
        elif role == 'User':
            return redirect('/userhome')
        elif role == 'SubAdmin':
            return redirect('/subadminhome')
        elif role == 'SuperAdmin':
            return redirect('/superadminhome')
    flash('Invalid credentials', 'danger')
    return redirect(url_for('user.user_login_page'))

@user_bp.route('/userlogout')
def user_logout():
    session.clear()
    return redirect(url_for('user.user_login_page'))

@user_bp.route('/useraccount')
def user_account():
    return render_template('UserAccount.html')

@user_bp.route('/EdituserProfile', methods=['POST'])
def update_user_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user.user_login_page'))
    update_doc = {
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'email': request.form.get('email'),
        'contactno': request.form.get('contactno'),
        'address': request.form.get('address'),
        'gender': request.form.get('gender'),
        'role': request.form.get('role')
    }
    if request.form.get('password'):
        update_doc['password'] = request.form.get('password')
    if request.form.get('confirm_password'):
        update_doc['confirm_password'] = request.form.get('confirm_password')
    current_app.mongo_db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update_doc})
    # Update session
    session['user_firstname'] = update_doc.get('first_name')
    session['user_lastname'] = update_doc.get('last_name')
    session['user_email'] = update_doc.get('email')
    session['user_phone'] = update_doc.get('contactno')
    session['user_address'] = update_doc.get('address')
    session['user_gender'] = update_doc.get('gender')
    session['user_role'] = update_doc.get('role', session.get('user_role'))
    return redirect(url_for('user.user_account'))

@user_bp.route('/users')
@admin_required
def list_users():
    users = list(current_app.mongo_db.users.find())
    for u in users:
        if u.get('_id') is not None:
            u['id'] = str(u['_id'])
    return render_template('users.html', users=users)

@user_bp.route('/users/change-role/<user_id>', methods=['POST'])
@admin_required
def change_role(user_id):
    new_role = request.form.get('role')
    if new_role in ['Admin', 'User', 'SuperAdmin', 'SubAdmin']:
        current_app.mongo_db.users.update_one({'_id': ObjectId(user_id)}, {'$set': {'role': new_role}})
        flash(f"Role updated to {new_role}", 'success')
    else:
        flash('Invalid role selected.', 'danger')
    return redirect(url_for('user.list_users'))

# Add more routes for booking, password reset, etc. as needed