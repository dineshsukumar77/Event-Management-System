from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from functools import wraps
import os
import json
from app.routes import hotel

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/userhome')
def userhome():
    return render_template('Userhome.html')

@main.route('/contactus')
def contactus():
    return render_template('ContactUs.html')

@main.route('/aboutus')
def aboutus():
    return render_template('Aboutus.html')

@main.route('/signup')
def signup():
    return render_template('UserRegisteration.html')

@main.route('/adminhome')
def adminhome():
    return render_template('adminhome.html')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('user_role') not in ['Admin', 'SuperAdmin']:
            flash('Admin access required.', 'danger')
            return redirect(url_for('user.user_login_page'))
        return f(*args, **kwargs)
    return decorated


@main.route('/admin/export-json', methods=['POST'])
@admin_required
def admin_export_json():
    db = current_app.mongo_db
    data_dir = os.path.join(current_app.root_path, '..', 'data')
    data_dir = os.path.abspath(data_dir)
    os.makedirs(data_dir, exist_ok=True)
    collections = ['users', 'events', 'hotels', 'caterings', 'vendors', 'bookings']
    def default(o):
        try:
            from bson import ObjectId
            if isinstance(o, ObjectId):
                return str(o)
        except Exception:
            pass
        # Serialize datetime/date to ISO strings
        import datetime as _dt
        if isinstance(o, (_dt.datetime, _dt.date)):
            return o.isoformat()
        raise TypeError
    for name in collections:
        docs = list(db[name].find())
        out_path = os.path.join(data_dir, f'{name}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(docs, f, ensure_ascii=False, indent=2, default=default)
    flash('Exported collections to data/ folder.', 'success')
    return redirect(url_for('main.adminhome'))


@main.route('/admin/import-json', methods=['POST'])
@admin_required
def admin_import_json():
    db = current_app.mongo_db
    data_dir = os.path.join(current_app.root_path, '..', 'data')
    data_dir = os.path.abspath(data_dir)
    collections = ['users', 'events', 'hotels', 'caterings', 'vendors', 'bookings']
    from bson import ObjectId
    for name in collections:
        path = os.path.join(data_dir, f'{name}.json')
        if not os.path.isfile(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            try:
                docs = json.load(f)
            except Exception:
                docs = []
        # try to coerce _id back to ObjectId if string
        for d in docs:
            if isinstance(d, dict) and '_id' in d and isinstance(d['_id'], str):
                try:
                    d['_id'] = ObjectId(d['_id'])
                except Exception:
                    pass
        if docs:
            db[name].delete_many({})
            db[name].insert_many(docs)
    flash('Imported data from data/ folder into MongoDB.', 'success')
    return redirect(url_for('main.adminhome'))