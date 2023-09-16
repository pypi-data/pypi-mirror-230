
"""This module is loaded by DjangoLDP core during setup."""

# define an extra variable (should be prefix with package name)
MYPACKAGE_VAR = 'MY_DEFAULT_VAR'

# register an extra middleware
MIDDLEWARE = []

# register an extra installed app
INSTALLED_APPS = []

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

REGISTRATION_USER_FORM='djangoldp_needle.form.NeedleUserForm'