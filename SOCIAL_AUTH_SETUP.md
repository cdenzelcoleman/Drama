# Social Authentication Setup Guide

This guide will help you set up Google, Facebook, and GitHub OAuth authentication for your Drama application.

## Prerequisites

1. Make sure you have updated your `.env` file with the OAuth credentials
2. Run database migrations: `python manage.py migrate`
3. Create a superuser: `python manage.py createsuperuser`

## Provider Setup Instructions

### Google OAuth Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select an existing one

2. **Enable APIs**
   - Go to "APIs & Services" > "Library"
   - Search for and enable "Google+ API" and "Google OAuth2 API"

3. **Create OAuth Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/accounts/google/login/callback/`
     - `http://127.0.0.1:8000/accounts/google/login/callback/`
     - Add your production domain when deploying

4. **Update .env file**
   ```env
   GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
   GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
   ```

### Facebook OAuth Setup

1. **Go to Facebook Developers**
   - Visit: https://developers.facebook.com/
   - Create a new app or use an existing one

2. **Add Facebook Login Product**
   - In your app dashboard, click "Add Product"
   - Choose "Facebook Login" and set it up

3. **Configure OAuth Settings**
   - Go to Facebook Login > Settings
   - Add Valid OAuth Redirect URIs:
     - `http://localhost:8000/accounts/facebook/login/callback/`
     - `http://127.0.0.1:8000/accounts/facebook/login/callback/`

4. **Get App Credentials**
   - Go to Settings > Basic
   - Copy your App ID and App Secret

5. **Update .env file**
   ```env
   FACEBOOK_APP_ID=your-facebook-app-id
   FACEBOOK_APP_SECRET=your-facebook-app-secret
   ```

### GitHub OAuth Setup

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/applications/new
   - Or go to Settings > Developer settings > OAuth Apps

2. **Register New OAuth App**
   - Application name: "Drama App"
   - Homepage URL: `http://localhost:8000`
   - Authorization callback URL: `http://localhost:8000/accounts/github/login/callback/`

3. **Get Client Credentials**
   - After creating the app, copy the Client ID
   - Generate a new client secret

4. **Update .env file**
   ```env
   GITHUB_CLIENT_ID=your-github-client-id
   GITHUB_CLIENT_SECRET=your-github-client-secret
   ```

## Django Admin Configuration

After setting up the OAuth apps, you need to configure them in Django admin:

1. **Start your Django server**
   ```bash
   python manage.py runserver
   ```

2. **Access Django Admin**
   - Go to: `http://localhost:8000/admin/`
   - Login with your superuser credentials

3. **Configure Social Applications**
   - Go to "Social Applications" under "SOCIAL ACCOUNTS"
   - Click "Add Social Application"
   
   **For each provider, create a new Social Application:**
   
   **Google:**
   - Provider: Google
   - Name: Google
   - Client id: (your Google client ID)
   - Secret key: (your Google client secret)
   - Sites: Select your site (usually "example.com")
   
   **Facebook:**
   - Provider: Facebook
   - Name: Facebook
   - Client id: (your Facebook app ID)
   - Secret key: (your Facebook app secret)
   - Sites: Select your site
   
   **GitHub:**
   - Provider: GitHub
   - Name: GitHub
   - Client id: (your GitHub client ID)
   - Secret key: (your GitHub client secret)
   - Sites: Select your site

## Testing

1. **Visit the login page**: `http://localhost:8000/accounts/login/`
2. **Try social authentication**: Click on the Google, Facebook, or GitHub buttons
3. **Check user creation**: New users should be created automatically when they sign in with social accounts

## Production Setup

When deploying to production:

1. **Update OAuth app settings** with your production domain
2. **Update redirect URIs** to use HTTPS and your production domain
3. **Update .env file** with production OAuth credentials
4. **Configure Django admin** with production social applications

## Troubleshooting

### Common Issues:

1. **"Invalid redirect_uri"**
   - Make sure your redirect URIs match exactly in both OAuth app settings and Django admin
   - Check for trailing slashes

2. **"Client not found"**
   - Verify your client ID and secret are correct
   - Make sure the Social Application is configured in Django admin

3. **"Site not found"**
   - Make sure you've selected the correct site in the Social Application settings
   - Check your SITE_ID setting in Django settings

4. **CSS not loading**
   - Run `python manage.py collectstatic`
   - Make sure STATIC_URL and STATICFILES_DIRS are configured correctly

## Security Notes

- Never commit OAuth secrets to version control
- Use environment variables for all sensitive data
- Enable HTTPS in production
- Regularly rotate OAuth secrets
- Monitor OAuth app usage in provider dashboards