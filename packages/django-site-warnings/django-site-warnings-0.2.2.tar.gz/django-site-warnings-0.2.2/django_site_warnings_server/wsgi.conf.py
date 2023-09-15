import os

bind = ["0.0.0.0:8061"]
workers = 2
threads = 40
daemon = True
accesslog = os.path.abspath(os.path.join(os.getcwd(), "../logs/gunicorn.access.log"))
errorlog = os.path.abspath(os.path.join(os.getcwd(), "../logs/gunicorn.error.log"))
keepalive = 300
timeout = 300
graceful_timeout = 300
loglevel = "info"
