# ArrowGlue
Commutative diagrams

## Developer To-Do Notes:

### Minor GUI bugs:
1. Standardize the menu-item hover color to something that matches closely
 but darker to the gold-yellow in the sketch editor page.  Always check
 in MS Edge - the hover colors are showing up differently in the browser test.
2. 

### Desired features:
1. Customize the default error views:
 https://docs.djangoproject.com/en/5.1/topics/http/views/#customizing-error-views

### Deployment considerations:
_https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/_
1. Should we use Django's Caching feature?  
 https://docs.djangoproject.com/en/5.1/ref/settings/#std-setting-CACHES
2. Set up a proper production database (not SQLite):
 https://docs.djangoproject.com/en/5.1/ref/settings/#std-setting-DATABASES
3. Set up email sending:
 https://docs.djangoproject.com/en/5.1/ref/settings/#std-setting-EMAIL_BACKEND
4. Get notified of site errors: 
 LOGGING / ADMINS / MANAGERS settings
5. Read through the Whitenoise + Django article:
 https://whitenoise.readthedocs.io/en/stable/django.html
6. Change the secret key in the environment vars both in the local .wpu (Wing project user file)
as well as Heroku app's settings.
 
### Performance considerations:
1. Consider using cached sessions to improve performance.
 https://docs.djangoproject.com/en/5.1/topics/http/sessions/#cached-sessions-backend
2. CONN_MAX_AGE setting
 https://docs.djangoproject.com/en/5.1/ref/databases/#persistent-database-connections
3. TEMPLATES setting
Enabling the cached template loader often improves performance drastically, as it avoids compiling 
each template every time it needs to be rendered. When DEBUG = False, the cached template loader is 
enabled automatically. See django.template.loaders.cached.Loader for more information.
4. 