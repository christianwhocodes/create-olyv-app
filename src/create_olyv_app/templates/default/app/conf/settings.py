"""
Custom Django settings extending the OLYV framework base configuration.
This file defines site-specific settings and overrides for The Spark Playhouse.
"""

from decouple import config
from olyv.conf import settings
from olyv.utils import static_url
from split_settings.tools import include

# ------------------------------------------------------------------------------
# 🎯 BASE CONFIGURATION
# ------------------------------------------------------------------------------

# Import foundational settings from OLYV framework
include(settings.OLYV_SETTINGS_PATH)

# ------------------------------------------------------------------------------
# 🛡️  SECURITY & ENVIRONMENT
# ------------------------------------------------------------------------------

DEBUG = config("DEBUG", default=True, cast=bool)
SECRET_KEY = config("SECRET_KEY", default="keep-the-SECRET_KEY-used-in-production-secret!")

# ------------------------------------------------------------------------------
# 🌐 ROUTING & URLS
# https://docs.djangoproject.com/en/stable/ref/settings/#root-urlconf
# ------------------------------------------------------------------------------

ROOT_URLCONF = "app.conf.urls"

# ------------------------------------------------------------------------------
# 🧵 Deployment
# https://docs.djangoproject.com/en/stable/ref/settings/#wsgi-application
# ------------------------------------------------------------------------------

WSGI_APPLICATION = "app.conf.wsgi.application"

# ------------------------------------------------------------------------------
# 🏠 ALLOWED HOSTS
# ------------------------------------------------------------------------------
# Extend olyv allowed hosts with production domains

ALLOWED_HOSTS = settings.ALLOWED_HOSTS + [
    "3000.christianwhocodes.space",
    "8000.christianwhocodes.space",
    "www.thesparkplayhouse.info",
]

# ------------------------------------------------------------------------------
# 📱 APPLICATION REGISTRY
# ------------------------------------------------------------------------------
# Extend olyv Installed apps with Custom applications for The Spark Playhouse

INSTALLED_APPS = settings.INSTALLED_APPS + [
    "app.home",
    "app.school",
    "app.seed",
]

# ------------------------------------------------------------------------------
# 🎨 BRANDING & VISUAL IDENTITY
# ------------------------------------------------------------------------------

SITE_NAME = "The Spark Playhouse"
SITE_DESCRIPTION = "Moving Towards the Best"
SITE_LOGO = static_url("home/site/logo-512.png", settings.STATIC_URL)
SITE_HERO_1 = static_url("home/site/hero-1.jpg", settings.STATIC_URL)
SITE_FAVICON = static_url("home/site/favicon-32.ico", settings.STATIC_URL)
SITE_APPLE_TOUCH_ICON = static_url("home/site/apple-180.png", settings.STATIC_URL)
SITE_ANDROID_CHROME_ICON = static_url("home/site/android-chrome-192.png", settings.STATIC_URL)
SITE_MSTILE = static_url("home/site/mstile-150.png", settings.STATIC_URL)

# ------------------------------------------------------------------------------
# 📧 EMAIL CONFIGURATION
# ------------------------------------------------------------------------------

EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "contact@thesparkplayhouse.info"
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default=None)

# Default sender for system emails
DEFAULT_FROM_EMAIL = f"The Spark Playhouse f<{EMAIL_HOST_USER}>"
SERVER_EMAIL = "The Spark Playhouse Server <server@thesparkplayhouse.info>"

# ------------------------------------------------------------------------------
# ADMINS
# ------------------------------------------------------------------------------

ADMINS = [("The Spark Admin", "admin@thesparkplayhouse.info")]

# ------------------------------------------------------------------------------
# 🔐 AUTHENTICATION & USER MANAGEMENT
# ------------------------------------------------------------------------------

# 🚧 Future authentication customizations
# Uncomment and configure when implementing custom user flows

# Custom username field configuration
# AUTH_USERNAME = {
#     "label": "Username or Email",
#     "placeholder": "Enter your username or email address",
#     "help_text": "You can use either your username or email to sign in",
# }


# ------------------------------------------------------------------------------
# 🎯 END OF CONFIGURATION
# ------------------------------------------------------------------------------
