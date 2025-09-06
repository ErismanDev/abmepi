# Gunicorn configuration file for ABMEPI

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/opt/abmepi/logs/gunicorn_access.log"
errorlog = "/opt/abmepi/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "abmepi_gunicorn"

# Server mechanics
daemon = False
pidfile = "/opt/abmepi/gunicorn.pid"
user = "abmepi"
group = "abmepi"
tmp_upload_dir = None

# SSL (uncomment when SSL is configured)
# keyfile = "/etc/nginx/ssl/key.pem"
# certfile = "/etc/nginx/ssl/cert.pem"

# Preload app for better performance
preload_app = True

# Worker timeout
worker_tmp_dir = "/dev/shm"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Environment variables
raw_env = [
    'DJANGO_SETTINGS_MODULE=abmepi.settings_production',
]

# Graceful timeout
graceful_timeout = 30

# Forwarded allow ips
forwarded_allow_ips = "*"

# Secure scheme header
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
