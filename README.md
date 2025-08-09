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

5. **Initialize the database**
   ```bash
   flask init-db
   ```

## Usage

### Running the Application

1. **Start the Flask development server**
   ```bash
   flask run
   ```

2. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - The application will be available at the local development server

### Available Routes

- `/` - Home page with login/register options
- `/login` - User login page
- `/register` - User registration page
- `/dashboard` - Protected dashboard (requires authentication)
- `/deliveries` - Deliveries management page
- `/forgot` - Password reset request page
- `/reset_password/<token>` - Password reset page

## Project Structure

```
test_login/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── schema.sql            # Database schema
├── Procfile              # Heroku deployment configuration
├── static/               # Static files (CSS, JS, images)
│   └── styles.css        # Custom styles
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # Dashboard page
│   ├── deliveries.html   # Deliveries page
│   ├── forgot.html       # Password reset request
│   └── reset_password.html # Password reset form
└── instance/             # Instance-specific files
    └── app.db           # SQLite database
```

## Configuration

### Environment Variables

The application uses the following environment variables:

- `SECRET_KEY` - Secret key for session management (auto-generated if not set)
- `MAIL_SERVER` - SMTP server for email functionality
- `MAIL_PORT` - SMTP port
- `MAIL_USE_TLS` - Use TLS for email
- `MAIL_USERNAME` - Email username
- `MAIL_PASSWORD` - Email password

### Database

The application uses SQLite as the default database. The database file is created automatically in the `instance/` directory.

## Development

### Adding New Features

1. **Create new routes** in `app.py`
2. **Add templates** in the `templates/` directory
3. **Update styles** in `static/styles.css`
4. **Test your changes** by running the application

### Database Changes

If you need to modify the database schema:

1. **Update `schema.sql`** with your changes
2. **Reinitialize the database**:
   ```bash
   flask init-db
   ```

## Deployment

### Heroku Deployment

The project includes a `Procfile` for easy deployment to Heroku:

1. **Create a Heroku app**
2. **Set environment variables** in Heroku dashboard
3. **Deploy using Git**:
   ```bash
   git push heroku main
   ```

### Other Platforms

The application can be deployed to any platform that supports Python/Flask applications.

## Security Features

- **Password Hashing**: Passwords are securely hashed using Werkzeug
- **Session Management**: Secure session handling
- **CSRF Protection**: Built-in CSRF protection
- **Input Validation**: Form validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.
