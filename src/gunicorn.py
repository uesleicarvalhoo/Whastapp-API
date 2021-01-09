from src.settings import HOST, PORT, WORKERS

bind = f"{HOST}:{PORT}"
workers = WORKERS
worker_connections = 1000
max_requests = int(workers * worker_connections)
max_requests_jitter = 5
keepalive = 120
timeout = 120
worker_class = "uvicorn.workers.UvicornWorker"
