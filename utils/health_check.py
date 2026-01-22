import json
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from utils.logger import get_logger

logger = get_logger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check endpoint"""
    
    # Class variable to store bot status
    bot_status = {
        'status': 'starting',
        'last_check': None,
        'last_price': None,
        'last_error': None,
        'uptime_start': datetime.now().isoformat(),
        'total_checks': 0,
        'total_alerts': 0,
        'total_errors': 0,
    }
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health' or self.path == '/':
            self.send_health_response()
        elif self.path == '/metrics':
            self.send_metrics_response()
        else:
            self.send_error(404, "Not Found")
    
    def send_health_response(self):
        """Send health check response"""
        status = self.bot_status.copy()
        
        # Determine if healthy
        is_healthy = status['status'] == 'running'
        
        response = {
            'status': 'healthy' if is_healthy else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'details': status
        }
        
        self.send_response(200 if is_healthy else 503)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def send_metrics_response(self):
        """Send metrics in Prometheus format"""
        status = self.bot_status
        
        metrics = f"""# HELP shb_bot_status Bot status (1=running, 0=stopped)
# TYPE shb_bot_status gauge
shb_bot_status{{symbol="SHB"}} {1 if status['status'] == 'running' else 0}

# HELP shb_bot_total_checks Total number of price checks
# TYPE shb_bot_total_checks counter
shb_bot_total_checks {status['total_checks']}

# HELP shb_bot_total_alerts Total number of alerts sent
# TYPE shb_bot_total_alerts counter
shb_bot_total_alerts {status['total_alerts']}

# HELP shb_bot_total_errors Total number of errors
# TYPE shb_bot_total_errors counter
shb_bot_total_errors {status['total_errors']}

# HELP shb_bot_last_price Last fetched stock price
# TYPE shb_bot_last_price gauge
shb_bot_last_price{{symbol="SHB"}} {status['last_price'] or 0}
"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; version=0.0.4')
        self.end_headers()
        self.wfile.write(metrics.encode())
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.debug(f"Health check: {format % args}")

class HealthCheckServer:
    """Health check HTTP server running in background thread"""
    
    def __init__(self, port=8080, enabled=True):
        self.port = port
        self.enabled = enabled
        self.server = None
        self.thread = None
    
    def start(self):
        """Start health check server in background thread"""
        if not self.enabled:
            logger.info("Health check server disabled")
            return
        
        try:
            self.server = HTTPServer(('0.0.0.0', self.port), HealthCheckHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info(f"Health check server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")
    
    def stop(self):
        """Stop health check server"""
        if self.server:
            self.server.shutdown()
            logger.info("Health check server stopped")
    
    @staticmethod
    def update_status(status='running', last_price=None, error=None):
        """Update bot status"""
        HealthCheckHandler.bot_status['status'] = status
        HealthCheckHandler.bot_status['last_check'] = datetime.now().isoformat()
        
        if last_price is not None:
            HealthCheckHandler.bot_status['last_price'] = last_price
            HealthCheckHandler.bot_status['total_checks'] += 1
        
        if error:
            HealthCheckHandler.bot_status['last_error'] = str(error)
            HealthCheckHandler.bot_status['total_errors'] += 1
    
    @staticmethod
    def increment_alerts():
        """Increment alert counter"""
        HealthCheckHandler.bot_status['total_alerts'] += 1
