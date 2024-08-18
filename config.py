import os

CSRF_ENABLED = True
SECRET_KEY = "your-secret-key"
# Flask-AppBuilder configuration
APP_NAME = "PyMyRedis"
APP_ICON = "/static/img/logo-transparent.png"
APP_THEME = "yeti.css"
# SQLite database
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Google OAuth 2.0 configuration (if needed)
# GOOGLE_CLIENT_ID = "your-google-client-id"
# GOOGLE_CLIENT_SECRET = "your-google-client-secret"
