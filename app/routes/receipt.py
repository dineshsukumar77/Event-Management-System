from flask import Blueprint, render_template, session, redirect, url_for, flash, Response, current_app
from functools import wraps
from bson import ObjectId
from io import BytesIO
from xhtml2pdf import pisa
import datetime
import os


receipt = Blueprint('receipt', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('user.user_login_page'))
        return f(*args, **kwargs)
    return decorated_function


@receipt.route('/receipt/download/<booking_id>')
@login_required
def download_receipt(booking_id: str):
    user_id = session.get('user_id')
    booking = current_app.mongo_db.bookings.find_one({'_id': ObjectId(booking_id), 'user_id': user_id})
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('booking.view_bookings'))

    # Normalize fields used in template
    if booking.get('_id') is not None:
        booking['id'] = str(booking['_id'])
    ev = booking.get('event_date')
    if isinstance(ev, str):
        try:
            booking['event_date'] = datetime.datetime.fromisoformat(ev)
        except Exception:
            pass
    # Attach user info if available in session
    booking['user_first_name'] = session.get('user_firstname')
    booking['user_last_name'] = session.get('user_lastname')
    booking['user_email'] = session.get('user_email')
    booking['user_contactno'] = session.get('user_phone')

    is_proforma = booking.get('payment_status') != 1
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')

    html = render_template('receipt.html', booking=booking, is_proforma=is_proforma, generated_on=today_str)

    pdf_io = BytesIO()
    pisa.CreatePDF(src=html, dest=pdf_io)
    pdf_io.seek(0)

    filename = f"{'Proforma-' if is_proforma else ''}Receipt-Booking-{booking_id}.pdf"
    return Response(
        pdf_io.read(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )


