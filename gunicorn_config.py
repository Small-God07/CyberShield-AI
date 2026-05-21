# ============================================
# ⚙️ Gunicorn Configuration pour Windows Server
# ============================================

import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# ========== SERVEUR ==========
bind = f"{os.getenv('SERVER_HOST', '0.0.0.0')}:{os.getenv('SERVER_PORT', '8000')}"
workers = int(os.getenv('SERVER_WORKERS', '4'))
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# ========== TIMEOUTS ==========
timeout = 120
graceful_timeout = 30
keepalive = 5

# ========== LOGGING ==========
accesslog = str(LOG_DIR / 'access.log')
errorlog = str(LOG_DIR / 'error.log')
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ========== APPLICATION ==========
app_name = 'CyberShield-AI'
proc_name = 'gunicorn-cybershield'
default_proc_name = 'gunicorn-cybershield'

# ========== SÉCURITÉ ==========
forwarded_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED_PROTOCOL': 'ssl',
    'X-FORWARDED_PROTO': 'https',
    'X-FORWARDED_SSL': 'on',
}

# ========== PERFORMANCE ==========
preload_app = True
daemon = False
umask = 0o022
tmp_upload_dir = None

# ========== CALLBACKS ==========
def on_starting(server):
    """Appelé au démarrage du serveur"""
    print(f"🚀 CyberShield-AI démarrage sur {bind}")

def when_ready(server):
    """Appelé quand le serveur est prêt"""
    print(f"✅ CyberShield-AI prêt à recevoir les requêtes !")

def on_exit(server):
    """Appelé à l'arrêt du serveur"""
    print(f"🛑 CyberShield-AI arrêt...")
