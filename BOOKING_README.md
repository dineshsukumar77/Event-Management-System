# Event Management System - Booking Functionality

## Overview

The Event Management System now includes comprehensive booking functionality that allows users to create, manage, and track their event bookings after logging in.

## Features

### 🔐 Authentication & Security
- Login required for all booking operations
- Session-based user management
- Role-based access control
- Secure form handling

### 📅 Booking Management
- **Create New Bookings**: Complete booking form with event details, venue selection, and additional services
- **View All Bookings**: Dashboard showing all user bookings with status indicators
- **Edit Bookings**: Update existing booking details
- **Delete Bookings**: Remove bookings with confirmation
- **Booking Details**: Detailed view of individual bookings
- **Status Tracking**: Real-time booking and payment status

### 🏨 Services Integration
- **Event Types**: Wedding, Birthday Party, Corporate Event, Anniversary, Graduation Party
- **Venues**: Hotels and conference centers with pricing
- **Catering**: Various catering services with different price points
- **Additional Services**: Photographer, DJ, Makeup Artist, Decorator

### 💰 Payment & Status
- **Payment Status**: Track payment completion
- **Booking Status**: Pending, Accepted, Rejected
- **Timeline View**: Visual timeline of booking progress
- **Amount Calculation**: Automatic price calculation based on selected services

## How to Use

### 1. Login
```
Email: admin@exquisite.com
Password: admin123
```

### 2. Access Booking Features
After login, you'll see the enhanced user dashboard with three main options:
- **Create Booking**: Start a new event booking
- **View Bookings**: See all your existing bookings
- **My Account**: Manage your profile

### 3. Create a New Booking
1. Click "Create Booking" on the dashboard
2. Fill in event details:
   - Event date and time
   - Duration and number of guests
   - Total amount
3. Select services:
   - Event type (Wedding, Birthday, etc.)
   - Hotel/venue
   - Catering service
4. Add optional services:
   - Photographer details
   - DJ/Entertainment
   - Makeup Artist
   - Decorator
5. Submit the booking

### 4. Manage Bookings
- **View All**: See all your bookings with status indicators
- **View Details**: Click on any booking for detailed information
- **Edit**: Modify booking details
- **Delete**: Remove bookings (with confirmation)
- **Status**: Check booking and payment status

## Database Structure

### Booking Model
```python
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_date = db.Column(db.Date)
    start_at = db.Column(db.String(50))
    max_total_hour = db.Column(db.String(50))
    amount = db.Column(db.Integer)
    no_of_guest = db.Column(db.String(50))
    photographer_name_desc = db.Column(db.Text)
    dj_name_desc = db.Column(db.Text)
    makeupartist_name_desc = db.Column(db.Text)
    decorator_name_desc = db.Column(db.Text)
    current_date = db.Column(db.String(50))
    accept_status = db.Column(db.Integer)  # 0=Pending, 1=Accepted, 2=Rejected
    payment_status = db.Column(db.Integer)  # 0=Pending, 1=Paid, 2=Failed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    catering_id = db.Column(db.Integer, db.ForeignKey('catering.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
```

### Related Models
- **User**: User information and authentication
- **Event**: Event types (Wedding, Birthday, etc.)
- **Hotel**: Venues and locations
- **Catering**: Catering services
- **Vendor**: Additional service providers

## Routes

### Booking Routes (`/app/routes/booking.py`)
- `GET /bookings` - View all user bookings
- `GET /new-booking` - Show booking form
- `POST /create-booking` - Create new booking
- `GET /booking/<id>` - View booking details
- `GET /edit-booking/<id>` - Edit booking form
- `POST /update-booking/<id>` - Update booking
- `POST /delete-booking/<id>` - Delete booking
- `GET /booking-status/<id>` - View booking status

## Templates

### Booking Templates
- `bookings.html` - List all bookings
- `new_booking.html` - Create new booking form
- `booking_detail.html` - Detailed booking view
- `edit_booking.html` - Edit booking form
- `booking_status.html` - Status and timeline view

## Sample Data

The system includes sample data for testing:
- **5 Event Types**: Wedding, Birthday Party, Corporate Event, Anniversary, Graduation Party
- **5 Hotels/Venues**: Various locations with different price points
- **5 Catering Services**: Different catering options with pricing

## Security Features

- **Login Required**: All booking routes require authentication
- **User Isolation**: Users can only see their own bookings
- **Form Validation**: Server-side validation for all inputs
- **CSRF Protection**: Built-in Flask CSRF protection
- **Session Management**: Secure session handling

## Running the Application

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Database and Sample Data**:
   ```bash
   python create_test_user.py
   python create_sample_data.py
   ```

3. **Run the Application**:
   ```bash
   python run.py
   ```

4. **Access the Application**:
   - Open browser to `http://localhost:5000`
   - Login with: `admin@exquisite.com` / `admin123`
   - Navigate to booking features

## Features in Detail

### Auto-Calculation
The booking form automatically calculates total amounts based on selected services:
- Hotel/venue pricing
- Catering service pricing
- Minimum booking amount

### Status Management
- **Booking Status**: Tracks whether the booking is pending, accepted, or rejected
- **Payment Status**: Tracks payment completion
- **Visual Indicators**: Color-coded badges for easy status identification

### Timeline View
The booking status page includes a visual timeline showing:
- Booking creation
- Review process
- Confirmation/rejection
- Payment completion

### Responsive Design
All booking pages are mobile-responsive with:
- Bootstrap 4 styling
- FontAwesome icons
- Modern card-based layout
- Intuitive navigation

## Future Enhancements

- **Payment Integration**: Connect to payment gateways
- **Email Notifications**: Automated booking confirmations
- **Calendar Integration**: Sync with external calendars
- **Admin Panel**: Admin interface for managing bookings
- **Advanced Filtering**: Search and filter bookings
- **Booking Analytics**: Reports and statistics

## Support

For technical support or questions about the booking functionality, please refer to the main application documentation or contact the development team. 