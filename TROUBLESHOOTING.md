# Troubleshooting Guide

This guide helps resolve common issues when deploying and running the Flask Datta Able application.

## 🚨 Common Issues & Solutions

### 1. ModuleNotFoundError: No module named 'flask_migrate'

**Problem**: Missing Flask-Migrate dependency

**Solution**:
```bash
pip install flask-migrate
```

**Prevention**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### 2. BuildError: Could not build url for endpoint 'deliveries'

**Problem**: Old template files trying to use non-existent routes

**Solution**: Remove old template files that conflict with the new structure:
```bash
# Remove old template files
rm templates/base.html
rm templates/login.html
rm templates/register.html
rm templates/dashboard.html
rm templates/deliveries.html
rm templates/forgot.html
rm templates/reset_password.html

# Remove old app.py
rm app.py
```

### 3. Flask Process Already Running

**Problem**: Cannot install packages because Flask is running

**Solution**:
```bash
# Stop the Flask process
Ctrl+C

# Or kill the process
taskkill /f /im python.exe
```

### 4. Database Migration Issues

**Problem**: Database schema not updated

**Solution**:
```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 5. Port Already in Use

**Problem**: Port 5000 is already occupied

**Solution**:
```bash
# Use a different port
python run.py --port 5001

# Or kill the process using the port
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### 6. Template Not Found Errors

**Problem**: Jinja2 cannot find templates

**Solution**: Ensure templates are in the correct directory structure:
```
templates/
├── layouts/
│   └── base.html
├── authentication/
│   ├── login.html
│   └── register.html
├── deliveries/
│   └── index.html
└── pages/
    └── index.html
```

### 7. Static Files Not Loading

**Problem**: CSS/JS files not found

**Solution**:
```bash
# Build static assets
npm install
npm run build

# Or copy static files manually
cp -r static/assets/* static/
```

### 8. Authentication Issues

**Problem**: Login not working

**Solution**:
1. Check database connection
2. Verify user exists in database
3. Check password hashing
4. Ensure session configuration is correct

### 9. Deployment Issues

#### Koyeb Deployment

**Problem**: App fails to start

**Solution**:
1. Check `koyeb.yaml` configuration
2. Verify start command: `gunicorn --bind 0.0.0.0:5000 run:app`
3. Ensure all environment variables are set
4. Check build logs for dependency issues

#### Render Deployment

**Problem**: Build fails

**Solution**:
1. Check `render.yaml` configuration
2. Verify Python version in `runtime.txt`
3. Ensure all dependencies are in `requirements.txt`
4. Check build command: `pip install -r requirements.txt`

### 10. Database Connection Issues

**Problem**: Cannot connect to database

**Solution**:
1. Check database URL in environment variables
2. Ensure database file permissions
3. For SQLite: Check file path and permissions
4. For PostgreSQL/MySQL: Verify connection credentials

## 🔧 Development Environment Setup

### Fresh Installation

```bash
# Clone repository
git clone https://github.com/Davidzb16/testpage.git
cd testpage

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Set up environment variables
cp env.sample .env
# Edit .env with your configuration

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Run the application
python run.py
```

### Environment Variables

Create a `.env` file with:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///apps/db.sqlite3
```

## 🐛 Debug Mode

Enable debug mode for detailed error messages:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python run.py
```

## 📊 Logs and Monitoring

### View Application Logs

```bash
# Local development
python run.py

# Production with gunicorn
gunicorn --bind 0.0.0.0:5000 run:app --log-level debug
```

### Database Debugging

```bash
# Check database tables
flask shell
>>> from apps import db
>>> db.engine.table_names()

# Check specific table
>>> from apps.authentication.models import Users
>>> Users.query.all()
```

## 🔒 Security Issues

### Secret Key

**Problem**: Weak or missing secret key

**Solution**:
```python
import secrets
print(secrets.token_hex(32))
```

### CSRF Protection

**Problem**: CSRF token validation fails

**Solution**:
1. Ensure `SECRET_KEY` is set
2. Check form includes CSRF token
3. Verify `flask_wtf` is installed

## 🚀 Performance Issues

### Slow Loading

**Problem**: Application loads slowly

**Solution**:
1. Enable static file caching
2. Optimize database queries
3. Use production WSGI server (gunicorn)
4. Enable compression

### Memory Issues

**Problem**: High memory usage

**Solution**:
1. Check for memory leaks in views
2. Optimize database queries
3. Use connection pooling
4. Monitor with tools like `memory_profiler`

## 📞 Getting Help

1. **Check the logs** for detailed error messages
2. **Verify your environment** matches the requirements
3. **Test locally** before deploying
4. **Create a minimal reproduction** of the issue
5. **Check GitHub Issues** for similar problems

## 🔄 Reset Everything

If all else fails, start fresh:

```bash
# Remove all generated files
rm -rf __pycache__
rm -rf migrations
rm -rf instance
rm apps/db.sqlite3

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Reinitialize database
flask db init
flask db migrate -m "Fresh start"
flask db upgrade

# Run the application
python run.py
```

---

**Remember**: Always check the logs first - they usually contain the solution to your problem!
