# Flask Login System

A simple and secure Flask-based login system with user authentication, registration, and password reset functionality.

## Features

- **User Registration**: New users can create accounts
- **User Login**: Secure authentication system
- **Password Reset**: Email-based password reset functionality
- **Dashboard**: Protected dashboard for authenticated users
- **Deliveries Management**: Track and manage deliveries
- **Responsive Design**: Works on desktop and mobile devices

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd test_login
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   ```bash
   # Create a .env file with your configuration
   SECRET_KEY=your-secret-key-here
   ```

6. **Initialize the database**
   ```bash
   python -c "from app import init_db; init_db()"
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Usage

### Registration
1. Visit `/register` to create a new account
2. Fill in your details and submit
3. You'll be redirected to login

### Login
1. Visit `/login` to access your account
2. Enter your email and password
3. You'll be redirected to the dashboard

### Dashboard
- View your delivery statistics
- Add new deliveries
- Manage existing deliveries
- Update delivery status

### Password Reset
1. Visit `/forgot` if you forgot your password
2. Enter your email address
3. Check your email for reset instructions

## Database Schema

The application uses SQLite with the following tables:

- **users**: User accounts and authentication
- **deliveries**: Delivery tracking information
- **password_resets**: Password reset tokens

## Deployment

### Koyeb Deployment

1. **Connect your GitHub repository to Koyeb**
2. **Create a new Web Service**
3. **Configure the service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Environment Variables**: Add `SECRET_KEY`

### Local Production

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

## Project Structure

```
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # Dashboard page
│   ├── deliveries.html   # Deliveries management
│   ├── forgot.html       # Password reset request
│   └── reset_password.html # Password reset form
├── static/               # Static files
│   └── styles.css        # CSS styles
├── instance/             # Database files
├── requirements.txt      # Python dependencies
└── schema.sql           # Database schema
```

## Security Features

- **Password Hashing**: Secure password storage
- **Session Management**: Secure session handling
- **CSRF Protection**: Built-in CSRF protection
- **Input Validation**: Form validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
