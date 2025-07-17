import logging
import os
from datetime import datetime
import time

class MillisecondFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created)  # Conversion correcte en datetime
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

def setup_logging():
    """Configure le système de logging"""
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger('monitoring')
    logger.setLevel(logging.INFO)
    
    # Évite les handlers dupliqués
    if logger.handlers:
        return logger
    
    formatter = MillisecondFormatter(
        fmt='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S,%f'[:-3]  # Format avec millisecondes
    )
    
    file_handler = logging.FileHandler('logs/monitoring.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def log_event(message):
    """Enregistre un message dans les logs"""
    logger = logging.getLogger('monitoring')
    logger.info(message)