"""
Settings providing authentication options.
"""

AUTH_USER_MODEL = 'cms_qe_auth.User'

LOGIN_REDIRECT_URL = '/'

LOGIN_URL = '/auth/login'

CMS_QE_AUTH_ENABLED = False  # Enable cms_qe_auth registration.
