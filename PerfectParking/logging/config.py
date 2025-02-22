import os
import logging.config
from datetime import datetime
from elasticsearch import Elasticsearch
from pythonjsonlogger import jsonlogger

# Elasticsearch configuration
es_client = Elasticsearch([{
    'host': os.getenv('ELASTICSEARCH_HOST', 'localhost'),
    'port': int(os.getenv('ELASTICSEARCH_PORT', 9200))
}])

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')
        log_record['application'] = 'perfect_parking'

class ElasticsearchHandler(logging.Handler):
    def __init__(self, index_prefix='parking-logs'):
        super().__init__()
        self.index_prefix = index_prefix

    def emit(self, record):
        try:
            log_entry = self.format(record)
            index_name = f"{self.index_prefix}-{datetime.utcnow():%Y.%m.%d}"
            es_client.index(index=index_name, body=log_entry)
        except Exception as e:
            print(f"Failed to send log to Elasticsearch: {e}")

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': CustomJsonFormatter,
            'format': '%(timestamp)s %(level)s %(name)s %(message)s'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/perfect_parking.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'elasticsearch': {
            '()': ElasticsearchHandler,
            'formatter': 'json',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/error.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'json',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'elasticsearch'],
            'level': 'ERROR',
            'propagate': False,
        },
        'perfect_parking': {
            'handlers': ['console', 'file', 'elasticsearch'],
            'level': 'INFO',
            'propagate': False,
        },
        'perfect_parking.security': {
            'handlers': ['error_file', 'elasticsearch'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Initialize logging configuration
logging.config.dictConfig(LOGGING_CONFIG) 