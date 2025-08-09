# Koyeb Deployment Guide

This guide will walk you through deploying your Flask Login System to Koyeb.

## Prerequisites

1. **GitHub Account**: Your code is already pushed to GitHub
2. **Koyeb Account**: Sign up at [koyeb.com](https://koyeb.com)
3. **GitHub Repository**: Your Flask app is in `https://github.com/Davidzb16/testpage.git`

## Step-by-Step Deployment

### 1. Sign Up for Koyeb

1. Go to [koyeb.com](https://koyeb.com)
2. Click "Get Started" or "Sign Up"
3. Choose "Sign up with GitHub" for easy integration
4. Authorize Koyeb to access your GitHub repositories

### 2. Deploy Your Application

#### Option A: Deploy via Koyeb Dashboard

1. **Log into Koyeb Dashboard**
   - Go to [console.koyeb.com](https://console.koyeb.com)
   - Sign in with your account

2. **Create New App**
   - Click "Create App" button
   - Choose "GitHub" as your deployment method
   - Select your repository: `Davidzb16/testpage`

3. **Configure Your App**
   - **Name**: `flask-login-system` (or any name you prefer)
   - **Region**: Choose the closest region to your users (e.g., Frankfurt for Europe)
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:5000 app:app`

4. **Environment Variables**
   Add these environment variables:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secure-secret-key-here
   ```
   
   **Generate a secure SECRET_KEY**:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

5. **Deploy**
   - Click "Deploy" button
   - Wait for the build and deployment to complete (usually 2-5 minutes)

#### Option B: Deploy via Koyeb CLI

1. **Install Koyeb CLI**
   ```bash
   # Windows (using scoop)
   scoop install koyeb

   # Or download from: https://github.com/koyeb/koyeb-cli/releases
   ```

2. **Login to Koyeb**
   ```bash
   koyeb login
   ```

3. **Deploy using koyeb.yaml**
   ```bash
   koyeb app init flask-login-system --docker
   ```

### 3. Configure Custom Domain (Optional)

1. **In Koyeb Dashboard**:
   - Go to your app
   - Click "Settings" tab
   - Scroll to "Domains" section
   - Click "Add Domain"
   - Enter your custom domain (e.g., `login.yourdomain.com`)

2. **DNS Configuration**:
   - Add a CNAME record pointing to your Koyeb app URL
   - Example: `login.yourdomain.com` → `flask-login-system-yourusername.koyeb.app`

### 4. Environment Variables for Production

For a production deployment, consider adding these environment variables:

```
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 5. Database Configuration

The app currently uses SQLite for simplicity. For production, consider:

1. **PostgreSQL on Koyeb**:
   - Create a PostgreSQL database in Koyeb
   - Update your app to use PostgreSQL
   - Add database connection environment variables

2. **External Database**:
   - Use services like PlanetScale, Supabase, or Railway
   - Update database connection settings

## Monitoring and Logs

### View Logs
1. Go to your app in Koyeb Dashboard
2. Click "Logs" tab
3. Monitor for any errors or issues

### Health Checks
- Your app automatically includes health checks
- Koyeb will restart your app if it becomes unhealthy

## Scaling

### Automatic Scaling
- Koyeb automatically scales your app based on traffic
- Free tier includes basic scaling

### Manual Scaling
1. Go to your app settings
2. Adjust the number of instances
3. Choose different instance sizes as needed

## Troubleshooting

### Common Issues

1. **Build Fails**:
   - Check that all dependencies are in `requirements.txt`
   - Ensure `gunicorn` is included
   - Verify Python version in `runtime.txt`

2. **App Won't Start**:
   - Check logs for error messages
   - Verify start command: `gunicorn --bind 0.0.0.0:5000 app:app`
   - Ensure port 5000 is correct

3. **Database Issues**:
   - SQLite file permissions in production
   - Consider switching to PostgreSQL for production

### Getting Help

- **Koyeb Documentation**: [docs.koyeb.com](https://docs.koyeb.com)
- **Koyeb Community**: [community.koyeb.com](https://community.koyeb.com)
- **GitHub Issues**: Create an issue in your repository

## Security Considerations

1. **SECRET_KEY**: Always use a strong, unique secret key
2. **HTTPS**: Koyeb automatically provides HTTPS
3. **Environment Variables**: Never commit sensitive data to Git
4. **Database**: Use secure database connections in production

## Cost Optimization

- **Free Tier**: Includes 2 apps, 256MB RAM, shared CPU
- **Paid Plans**: Start at $5/month for more resources
- **Auto-scaling**: Only pay for what you use

## Next Steps

After successful deployment:

1. **Test Your App**: Visit your Koyeb URL and test all features
2. **Set Up Monitoring**: Configure alerts and monitoring
3. **Backup Strategy**: Set up database backups
4. **CI/CD**: Consider setting up automatic deployments from GitHub

## Your App URL

Once deployed, your app will be available at:
```
https://flask-login-system-yourusername.koyeb.app
```

Replace `yourusername` with your actual Koyeb username.
