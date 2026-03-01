from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from bson import ObjectId
from functools import wraps
import os
from werkzeug.utils import secure_filename

vendor_bp = Blueprint('vendor', __name__)

UPLOAD_FOLDER = 'app/static/images/vendors/'
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

@vendor_bp.route('/vendors')
@admin_required
def list_vendors():
    vendors = list(current_app.mongo_db.vendors.find())
    for v in vendors:
        if v.get('_id') is not None:
            v['id'] = str(v['_id'])
    return render_template('vendors.html', vendors=vendors)

@vendor_bp.route('/vendors/add', methods=['GET', 'POST'])
@admin_required
def add_vendor():
    if request.method == 'POST':
        name = request.form.get('vendorname')
        desc = request.form.get('vendor_desc')
        location = request.form.get('vendor_location')
        price = request.form.get('vendor_price')
        img_path = ''
        if 'vendor_img' in request.files:
            file = request.files['vendor_img']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                img_path = f'images/vendors/{filename}'
        current_app.mongo_db.vendors.insert_one({
            'vendorname': name,
            'vendor_desc': desc,
            'vendor_location': location,
            'vendor_price': price,
            'vendor_img': img_path
        })
        flash('Vendor added successfully!', 'success')
        return redirect(url_for('vendor.list_vendors'))
    return render_template('add_vendor.html')

@vendor_bp.route('/vendors/edit/<vendor_id>', methods=['GET', 'POST'])
@admin_required
def edit_vendor(vendor_id):
    vendor = current_app.mongo_db.vendors.find_one({'_id': ObjectId(vendor_id)})
    if request.method == 'POST':
        update_doc = {
            'vendorname': request.form.get('vendorname'),
            'vendor_desc': request.form.get('vendor_desc'),
            'vendor_location': request.form.get('vendor_location'),
            'vendor_price': request.form.get('vendor_price')
        }
        if 'vendor_img' in request.files:
            file = request.files['vendor_img']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                update_doc['vendor_img'] = f'images/vendors/{filename}'
        current_app.mongo_db.vendors.update_one({'_id': ObjectId(vendor_id)}, {'$set': update_doc})
        flash('Vendor updated successfully!', 'success')
        return redirect(url_for('vendor.list_vendors'))
    return render_template('edit_vendor.html', vendor=vendor)

@vendor_bp.route('/vendors/delete/<vendor_id>', methods=['POST'])
@admin_required
def delete_vendor(vendor_id):
    current_app.mongo_db.vendors.delete_one({'_id': ObjectId(vendor_id)})
    flash('Vendor deleted successfully!', 'success')
    return redirect(url_for('vendor.list_vendors'))