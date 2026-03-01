from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from bson import ObjectId
from functools import wraps
import os
from werkzeug.utils import secure_filename

catering_bp = Blueprint('catering', __name__)

UPLOAD_FOLDER = 'app/static/images/catering/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] not in ['Admin', 'SuperAdmin']:
            flash('Admin access required.', 'danger')
            return redirect(url_for('user.user_login_page'))
        return f(*args, **kwargs)
    return decorated_function

@catering_bp.route('/catering')
def list_catering():
    catering = list(current_app.mongo_db.caterings.find())
    for c in catering:
        if c.get('_id') is not None:
            c['id'] = str(c['_id'])
    is_admin = session.get('user_role') in ['Admin', 'SuperAdmin']
    return render_template('catering.html', catering=catering, is_admin=is_admin)

@catering_bp.route('/catering/add', methods=['GET', 'POST'])
@admin_required
def add_catering():
    if request.method == 'POST':
        name = request.form.get('catername')
        desc = request.form.get('cater_desc')
        location = request.form.get('cater_location')
        price = request.form.get('cater_price')
        img_path = ''
        if 'cater_img' in request.files:
            file = request.files['cater_img']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                img_path = f'images/catering/{filename}'
        current_app.mongo_db.caterings.insert_one({
            'catername': name,
            'cater_desc': desc,
            'cater_location': location,
            'cater_price': price,
            'cater_img': img_path
        })
        flash('Buffet added successfully!', 'success')
        return redirect(url_for('catering.list_catering'))
    return render_template('add_catering.html')

@catering_bp.route('/catering/edit/<catering_id>', methods=['GET', 'POST'])
@admin_required
def edit_catering(catering_id):
    catering = current_app.mongo_db.caterings.find_one({'_id': ObjectId(catering_id)})
    if request.method == 'POST':
        update_doc = {
            'catername': request.form.get('catername'),
            'cater_desc': request.form.get('cater_desc'),
            'cater_location': request.form.get('cater_location'),
            'cater_price': request.form.get('cater_price')
        }
        if 'cater_img' in request.files:
            file = request.files['cater_img']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                update_doc['cater_img'] = f'images/catering/{filename}'
        current_app.mongo_db.caterings.update_one({'_id': ObjectId(catering_id)}, {'$set': update_doc})
        flash('Buffet updated successfully!', 'success')
        return redirect(url_for('catering.list_catering'))
    return render_template('edit_catering.html', catering=catering)

@catering_bp.route('/catering/delete/<catering_id>', methods=['POST'])
@admin_required
def delete_catering(catering_id):
    current_app.mongo_db.caterings.delete_one({'_id': ObjectId(catering_id)})
    flash('Buffet deleted successfully!', 'success')
    return redirect(url_for('catering.list_catering'))