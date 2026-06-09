# Procfile — tells Render/Railway/Heroku how to start your app
#
# web: the command to run for the web server
# gunicorn smartexpense.wsgi: load the WSGI app from smartexpense/wsgi.py
# --bind 0.0.0.0:$PORT: listen on all interfaces, on the port provided by the platform
# --workers 2: 2 worker processes (adjust based on RAM)
# --timeout 120: kill workers that take >120s (prevents hanging requests)
web: gunicorn smartexpense.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120
