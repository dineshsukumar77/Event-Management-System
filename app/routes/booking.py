from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from bson import ObjectId
from datetime import datetime
from functools import wraps

booking_bp = Blueprint('booking', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('user.user_login_page'))
        return f(*args, **kwargs)
    return decorated_function

@booking_bp.route('/bookings')
@login_required
def view_bookings():
    """View all bookings for the logged-in user"""
    user_id = session.get('user_id')
    bookings = list(current_app.mongo_db.bookings.find({'user_id': user_id}).sort('event_date', -1))
    # Normalize for templates: add id, convert event_date to datetime, attach names
    for b in bookings:
        if b.get('_id') is not None:
            b['id'] = str(b['_id'])
        # Convert ISO string to datetime for strftime
        ev = b.get('event_date')
        if isinstance(ev, str):
            try:
                b['event_date'] = datetime.fromisoformat(ev)
            except Exception:
                pass
        # Attach related names for display
        if b.get('event_id'):
            evt = current_app.mongo_db.events.find_one({'_id': ObjectId(b['event_id'])})
            if evt:
                b['event'] = {'eventname': evt.get('eventname')}
        if b.get('hotel_id'):
            ht = current_app.mongo_db.hotels.find_one({'_id': ObjectId(b['hotel_id'])})
            if ht:
                b['hotel'] = {'hotel_name': ht.get('hotel_name')}
        if b.get('catering_id'):
            ct = current_app.mongo_db.caterings.find_one({'_id': ObjectId(b['catering_id'])})
            if ct:
                b['catering'] = {'catername': ct.get('catername')}
    return render_template('bookings.html', bookings=bookings)

@booking_bp.route('/new-booking')
@login_required
def new_booking_form():
    """Show the new booking form"""
    hotels = list(current_app.mongo_db.hotels.find())
    for h in hotels:
        if h.get('_id') is not None:
            h['id'] = str(h['_id'])
    catering_services = list(current_app.mongo_db.caterings.find())
    for c in catering_services:
        if c.get('_id') is not None:
            c['id'] = str(c['_id'])
    events = list(current_app.mongo_db.events.find())
    for e in events:
        if e.get('_id') is not None:
            e['id'] = str(e['_id'])
    return render_template('new_booking.html', 
                         hotels=hotels, 
                         catering_services=catering_services, 
                         events=events)

@booking_bp.route('/create-booking', methods=['POST'])
@login_required
def create_booking():
    """Create a new booking"""
    try:
        user_id = session.get('user_id')
        
        # Get form data
        event_date = datetime.strptime(request.form.get('event_date'), '%Y-%m-%d').date()
        start_at = request.form.get('start_at')
        max_total_hour = request.form.get('max_total_hour')
        no_of_guest = request.form.get('no_of_guest')
        # Derive amount server-side from selected services to avoid client tampering
        amount = 0
        
        # Optional services
        photographer_name_desc = request.form.get('photographer_name_desc', '')
        dj_name_desc = request.form.get('dj_name_desc', '')
        makeupartist_name_desc = request.form.get('makeupartist_name_desc', '')
        decorator_name_desc = request.form.get('decorator_name_desc', '')
        
        # Foreign keys
        hotel_id = request.form.get('hotel_id')
        catering_id = request.form.get('catering_id')
        event_id = request.form.get('event_id')
        
        # Look up selected services for pricing
        if hotel_id:
            hotel = current_app.mongo_db.hotels.find_one({'_id': ObjectId(hotel_id)})
            if hotel:
                try:
                    amount += int(hotel.get('price') or 0)
                except Exception:
                    pass
        if catering_id:
            catering = current_app.mongo_db.caterings.find_one({'_id': ObjectId(catering_id)})
            if catering:
                try:
                    amount += int(catering.get('cater_price') or 0)
                except Exception:
                    pass
        if amount <= 0:
            amount = 100

        # Insert directly into MongoDB
        current_app.mongo_db.bookings.insert_one({
            'user_id': user_id,
            'event_date': event_date.isoformat() if event_date else None,
            'start_at': start_at,
            'max_total_hour': max_total_hour,
            'no_of_guest': no_of_guest,
            'amount': amount,
            'photographer_name_desc': photographer_name_desc,
            'dj_name_desc': dj_name_desc,
            'makeupartist_name_desc': makeupartist_name_desc,
            'decorator_name_desc': decorator_name_desc,
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'accept_status': 0,
            'payment_status': 0,
            'hotel_id': hotel_id if hotel_id else None,
            'catering_id': catering_id if catering_id else None,
            'event_id': event_id if event_id else None,
            'created_at': datetime.utcnow()
        })
        
        flash('Booking created successfully!', 'success')
        return redirect(url_for('booking.view_bookings'))
        
    except Exception as e:
        flash(f'Error creating booking: {str(e)}', 'danger')
        return redirect(url_for('booking.new_booking_form'))

@booking_bp.route('/booking/<booking_id>')
@login_required
def view_booking_detail(booking_id):
    """View detailed information about a specific booking"""
    user_id = session.get('user_id')
    booking = current_app.mongo_db.bookings.find_one({'_id': ObjectId(booking_id), 'user_id': user_id})
    
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('booking.view_bookings'))
    # normalize fields for templates
    if booking.get('_id') is not None:
        booking['id'] = str(booking['_id'])
    ev = booking.get('event_date')
    if isinstance(ev, str):
        try:
            booking['event_date'] = datetime.fromisoformat(ev)
        except Exception:
            pass
    return render_template('booking_detail.html', booking=booking)

@booking_bp.route('/edit-booking/<booking_id>')
@login_required
def edit_booking_form(booking_id):
    """Show the edit booking form"""
    user_id = session.get('user_id')
    booking = current_app.mongo_db.bookings.find_one({'_id': ObjectId(booking_id), 'user_id': user_id})
    
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('booking.view_bookings'))
    
    hotels = list(current_app.mongo_db.hotels.find())
    catering_services = list(current_app.mongo_db.caterings.find())
    events = list(current_app.mongo_db.events.find())
    
    return render_template('edit_booking.html', 
                         booking=booking,
                         hotels=hotels, 
                         catering_services=catering_services, 
                         events=events)

@booking_bp.route('/update-booking/<booking_id>', methods=['POST'])
@login_required
def update_booking(booking_id):
    """Update an existing booking"""
    try:
        user_id = session.get('user_id')
        booking = current_app.mongo_db.bookings.find_one({'_id': ObjectId(booking_id), 'user_id': user_id})
        
        if not booking:
            flash('Booking not found', 'danger')
            return redirect(url_for('booking.view_bookings'))
        
        hotel_id = request.form.get('hotel_id') or None
        catering_id = request.form.get('catering_id') or None
        # Recompute amount server-side
        new_amount = 0
        if hotel_id:
            hotel = current_app.mongo_db.hotels.find_one({'_id': ObjectId(hotel_id)})
            if hotel:
                try:
                    new_amount += int(hotel.get('price') or 0)
                except Exception:
                    pass
        if catering_id:
            catering = current_app.mongo_db.caterings.find_one({'_id': ObjectId(catering_id)})
            if catering:
                try:
                    new_amount += int(catering.get('cater_price') or 0)
                except Exception:
                    pass
        if new_amount <= 0:
            new_amount = 100

        update_doc = {
            'event_date': datetime.strptime(request.form.get('event_date'), '%Y-%m-%d').date().isoformat(),
            'start_at': request.form.get('start_at'),
            'max_total_hour': request.form.get('max_total_hour'),
            'no_of_guest': request.form.get('no_of_guest'),
            'amount': new_amount,
            'photographer_name_desc': request.form.get('photographer_name_desc', ''),
            'dj_name_desc': request.form.get('dj_name_desc', ''),
            'makeupartist_name_desc': request.form.get('makeupartist_name_desc', ''),
            'decorator_name_desc': request.form.get('decorator_name_desc', ''),
            'hotel_id': hotel_id,
            'catering_id': catering_id,
            'event_id': request.form.get('event_id') or None
        }
        current_app.mongo_db.bookings.update_one({'_id': ObjectId(booking_id), 'user_id': user_id}, {'$set': update_doc})
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('booking.view_bookings'))
        
    except Exception as e:
        flash(f'Error updating booking: {str(e)}', 'danger')
        return redirect(url_for('booking.edit_booking_form', booking_id=booking_id))

@booking_bp.route('/delete-booking/<booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):
    """Delete a booking"""
    try:
        user_id = session.get('user_id')
        booking = current_app.mongo_db.bookings.find_one({'_id': ObjectId(booking_id), 'user_id': user_id})
        
        if not booking:
            flash('Booking not found', 'danger')
            return redirect(url_for('booking.view_bookings'))
        
        current_app.mongo_db.bookings.delete_one({'_id': ObjectId(booking_id), 'user_id': user_id})
        flash('Booking deleted successfully!', 'success')
        return redirect(url_for('booking.view_bookings'))
        
    except Exception as e:
        flash(f'Error deleting booking: {str(e)}', 'danger')
        return redirect(url_for('booking.view_bookings'))

@booking_bp.route('/booking-status/<booking_id>')
@login_required
def booking_status(booking_id):
    """View booking status and payment information"""
    user_id = session.get('user_id')
    booking = current_app.mongo_db.bookings.find_one({'_id': ObjectId(booking_id), 'user_id': user_id})
    
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('booking.view_bookings'))
    # normalize for template
    if booking.get('_id') is not None:
        booking['id'] = str(booking['_id'])
    ev = booking.get('event_date')
    if isinstance(ev, str):
        try:
            booking['event_date'] = datetime.fromisoformat(ev)
        except Exception:
            pass
    return render_template('booking_status.html', booking=booking)