from flask import Blueprint, jsonify, request, session, redirect, url_for, flash, current_app
from functools import wraps
from bson import ObjectId
import os

try:
    import razorpay
except Exception:  # pragma: no cover
    razorpay = None


payment_bp = Blueprint('payment', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('user.user_login_page'))
        return f(*args, **kwargs)
    return decorated_function


def get_razorpay_client():
    key_id = os.getenv('RAZORPAY_KEY_ID')
    key_secret = os.getenv('RAZORPAY_KEY_SECRET')
    if not key_id or not key_secret:
        raise RuntimeError('Razorpay keys are not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET environment variables.')
    if razorpay is None:
        raise RuntimeError('razorpay package is not installed. Add "razorpay" to requirements and install dependencies.')
    return razorpay.Client(auth=(key_id, key_secret))


@payment_bp.route('/payment/create-order/<booking_id>', methods=['POST'])
@login_required
def create_order(booking_id: str):
    user_id = session.get('user_id')
    booking = current_app.mongo_db.bookings.find_one({'_id': ObjectId(booking_id), 'user_id': user_id})
    if booking is None:
        return jsonify({'error': 'Booking not found'}), 404
    if booking.get('payment_status') == 1:
        return jsonify({'error': 'Payment already completed'}), 400

    amount_paise = int(booking.get('amount', 0)) * 100
    client = get_razorpay_client()

    order = client.order.create(
        data={
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': f"booking_{booking_id}",
            'payment_capture': 1,
            'notes': {
                'booking_id': booking_id,
                'user_id': str(user_id),
            },
        }
    )

    return jsonify({
        'order_id': order.get('id'),
        'amount': amount_paise,
        'currency': 'INR',
        'key_id': os.getenv('RAZORPAY_KEY_ID'),
        'booking_id': booking_id,
        'user': {
            'name': f"{(booking.get('first_name') or '')} {(booking.get('last_name') or '')}".strip(),
            'email': booking.get('email', ''),
            'contact': booking.get('contactno', ''),
        }
    })


@payment_bp.route('/payment/verify', methods=['POST'])
@login_required
def verify_payment():
    client = get_razorpay_client()
    payload = {
        'razorpay_order_id': request.form.get('razorpay_order_id'),
        'razorpay_payment_id': request.form.get('razorpay_payment_id'),
        'razorpay_signature': request.form.get('razorpay_signature'),
    }
    booking_id = request.form.get('booking_id')

    if not all(payload.values()) or not booking_id:
        flash('Invalid payment verification payload.', 'danger')
        return redirect(url_for('booking.booking_status', booking_id=booking_id or '0'))

    try:
        client.utility.verify_payment_signature(payload)
    except Exception as ex:  # signature mismatch or error
        booking = current_app.mongo_db.bookings.find_one({'_id': ObjectId(booking_id), 'user_id': session.get('user_id')})
        if booking:
            current_app.mongo_db.bookings.update_one({'_id': ObjectId(booking_id)}, {'$set': {'payment_status': 2}})
        flash('Payment verification failed. Please try again.', 'danger')
        return redirect(url_for('booking.booking_status', booking_id=booking_id))

    booking = current_app.mongo_db.bookings.find_one({'_id': ObjectId(booking_id), 'user_id': session.get('user_id')})
    if not booking:
        flash('Booking not found after payment.', 'danger')
        return redirect(url_for('booking.view_bookings'))

    current_app.mongo_db.bookings.update_one({'_id': ObjectId(booking_id)}, {'$set': {'payment_status': 1}})

    flash('Payment successful! Your booking is confirmed.', 'success')
    return redirect(url_for('booking.booking_status', booking_id=booking_id))


