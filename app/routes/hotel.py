from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from bson import ObjectId
from functools import wraps
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'app/static/images/hotels/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

hotel_bp = Blueprint('hotel', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] not in ['Admin', 'SuperAdmin']:
            flash('Admin access required.', 'danger')
            return redirect(url_for('user.user_login_page'))
        return f(*args, **kwargs)
    return decorated_function

@hotel_bp.route('/hotels')
@admin_required
def list_hotels():
    hotels = list(current_app.mongo_db.hotels.find())
    for h in hotels:
        if h.get('_id') is not None:
            h['id'] = str(h['_id'])
    return render_template('hotels.html', hotels=hotels)

@hotel_bp.route('/hotels/add', methods=['GET', 'POST'])
@admin_required
def add_hotel():
    if request.method == 'POST':
        name = request.form.get('hotel_name')
        desc = request.form.get('hotel_desc')
        price = request.form.get('price')
        location = request.form.get('location')
        img_path = ''
        if 'hotel_img1' in request.files:
            file = request.files['hotel_img1']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                img_path = f'images/hotels/{filename}'
        current_app.mongo_db.hotels.insert_one({
            'hotel_name': name,
            'hotel_desc': desc,
            'hotel_img1': img_path,
            'price': price,
            'location': location
        })
        flash('Hotel added successfully!', 'success')
        return redirect(url_for('hotel.list_hotels'))
    return render_template('add_hotel.html')

@hotel_bp.route('/hotels/edit/<hotel_id>', methods=['GET', 'POST'])
@admin_required
def edit_hotel(hotel_id):
    hotel = current_app.mongo_db.hotels.find_one({'_id': ObjectId(hotel_id)})
    if request.method == 'POST':
        update_doc = {
            'hotel_name': request.form.get('hotel_name'),
            'hotel_desc': request.form.get('hotel_desc'),
            'price': request.form.get('price'),
            'location': request.form.get('location')
        }
        if 'hotel_img1' in request.files:
            file = request.files['hotel_img1']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                update_doc['hotel_img1'] = f'images/hotels/{filename}'
        current_app.mongo_db.hotels.update_one({'_id': ObjectId(hotel_id)}, {'$set': update_doc})
        flash('Hotel updated successfully!', 'success')
        return redirect(url_for('hotel.list_hotels'))
    return render_template('edit_hotel.html', hotel=hotel)

@hotel_bp.route('/hotels/delete/<hotel_id>', methods=['POST'])
@admin_required
def delete_hotel(hotel_id):
    current_app.mongo_db.hotels.delete_one({'_id': ObjectId(hotel_id)})
    flash('Hotel deleted successfully!', 'success')
    return redirect(url_for('hotel.list_hotels'))