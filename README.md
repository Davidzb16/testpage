# Flask Datta Able - Login & Deliveries System

A modern Flask application built on the **Flask Datta Able** template, featuring a comprehensive login system and deliveries management functionality.

## 🚀 Features

### Authentication System
- **User Registration**: Secure account creation with email validation
- **User Login**: Session-based authentication with remember me functionality
- **Password Reset**: Email-based password reset with secure tokens
- **OAuth Integration**: GitHub and Google OAuth support
- **Profile Management**: User profile editing and management

### Deliveries Management System
- **Delivery Tracking**: Add and manage delivery tracking numbers
- **Status Management**: Update delivery status (pending, delivered, cancelled)
- **Amount Tracking**: Track delivery amounts with proper currency handling
- **Statistics Dashboard**: Real-time statistics for delivery counts
- **Soft Delete**: Safe deletion with restore functionality
- **Demo Data**: Quick setup with sample delivery data

### Modern UI/UX
- **Bootstrap 5**: Responsive design that works on all devices
- **Datta Able Design**: Professional dashboard interface
- **Interactive Charts**: Visual data representation
- **Dynamic Tables**: Advanced data table functionality
- **Real-time Updates**: AJAX-powered interactions

## 🛠️ Technology Stack

- **Backend**: Flask 3.1.0
- **Database**: SQLAlchemy with SQLite (production-ready for PostgreSQL/MySQL)
- **Authentication**: Flask-Login with OAuth support
- **Frontend**: Bootstrap 5, Feather Icons, ApexCharts
- **Build Tools**: Vite for asset management
- **Deployment**: Docker, Gunicorn, Render-ready

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 16+ (for asset compilation)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Davidzb16/testpage.git
   cd testpage
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Install Node.js dependencies**
   ```bash
   npm install
   ```

6. **Set up environment variables**
   ```bash
   cp env.sample .env
   # Edit .env with your configuration
   ```

7. **Initialize database**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

8. **Run the application**
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5000`

## 🗄️ Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password`: Hashed password
- `bio`: User biography (optional)
- `oauth_github`: GitHub OAuth ID
- `oauth_google`: Google OAuth ID

### Deliveries Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `tracking_number`: Unique tracking number
- `amount_due`: Amount in cents (integer)
- `status`: Delivery status (pending/delivered/cancelled)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `deleted_at`: Soft delete timestamp

### Password Resets Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `token`: Secure reset token
- `expires_at`: Token expiration time
- `used_at`: Token usage timestamp
- `created_at`: Creation timestamp

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///apps/db.sqlite3

# OAuth Configuration (Optional)
GITHUB_OAUTH_CLIENT_ID=your-github-client-id
GITHUB_OAUTH_CLIENT_SECRET=your-github-client-secret
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Generate Secret Key

```python
import secrets
print(secrets.token_hex(32))
```

## 🚀 Deployment

### Render Deployment

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Configure the service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT run:app`
   - **Environment Variables**: Add all required environment variables

### Docker Deployment

```bash
# Build the image
docker build -t flask-datta-able .

# Run the container
docker run -p 5000:5000 flask-datta-able
```

### Local Production

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 run:app
```

## 📁 Project Structure

```
├── apps/                          # Application modules
│   ├── authentication/            # User authentication
│   ├── deliveries/                # Deliveries management
│   ├── home/                      # Main dashboard
│   ├── charts/                    # Chart components
│   ├── dyn_dt/                    # Dynamic tables
│   └── config.py                  # Configuration
├── templates/                     # Jinja2 templates
│   ├── layouts/                   # Base layouts
│   ├── includes/                  # Reusable components
│   ├── pages/                     # Page templates
│   ├── authentication/            # Auth templates
│   └── deliveries/                # Delivery templates
├── static/                        # Static assets
│   ├── assets/                    # CSS, JS, images
│   └── scss/                      # SCSS source files
├── migrations/                    # Database migrations
├── media/                         # User uploaded files
├── run.py                         # Application entry point
├── requirements.txt               # Python dependencies
└── package.json                   # Node.js dependencies
```

## 🔐 Security Features

- **Password Hashing**: Secure password storage with bcrypt
- **CSRF Protection**: Built-in CSRF token protection
- **Session Management**: Secure session handling
- **Input Validation**: Comprehensive form validation
- **SQL Injection Protection**: SQLAlchemy ORM protection
- **XSS Protection**: Template auto-escaping

## 🎨 Customization

### Adding New Modules

1. **Create a new blueprint**:
   ```bash
   mkdir apps/your_module
   touch apps/your_module/__init__.py
   touch apps/your_module/routes.py
   touch apps/your_module/models.py
   ```

2. **Register the blueprint** in `apps/__init__.py`

3. **Create templates** in `templates/your_module/`

### Styling

- **SCSS**: Edit `static/assets/scss/custom.scss`
- **CSS**: Edit `static/assets/css/custom.css`
- **Build**: Run `npm run build` to compile assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🙏 Acknowledgments

- **AppSeed**: Flask Datta Able template
- **CodedThemes**: Datta Able UI Kit
- **Bootstrap**: Frontend framework
- **Flask**: Web framework

## 📞 Support

- **Documentation**: [Flask Datta Able Docs](https://app-generator.dev/docs/products/flask/datta-able/index.html)
- **Issues**: [GitHub Issues](https://github.com/Davidzb16/testpage/issues)
- **Live Demo**: [Flask Datta Able Demo](https://flask-datta-demo.onrender.com)

---

**Built with ❤️ using Flask Datta Able**
