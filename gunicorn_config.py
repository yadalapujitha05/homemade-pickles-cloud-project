"""
Gunicorn Configuration for HomeMade Pickles & Snacks
Production WSGI server settings for AWS EC2 deployment.
"""

# Bind to all interfaces on port 5000 (Nginx will proxy from port 80)
bind = "0.0.0.0:5000"

# Number of worker processes
# Formula: (2 * CPU_cores) + 1
# For a t2.micro EC2 (1 vCPU): 3 workers
workers = 3

# Worker class: sync is fine for this project scale
worker_class = "sync"

# Timeout in seconds
timeout = 60

# Graceful timeout for worker restart
graceful_timeout = 30

# Access log to stdout (CloudWatch agent will capture it)
accesslog = "-"
errorlog  = "-"
loglevel  = "info"

# Process name
proc_name = "homemade_pickles"
