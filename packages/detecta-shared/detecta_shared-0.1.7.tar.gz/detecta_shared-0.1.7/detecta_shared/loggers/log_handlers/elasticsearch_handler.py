import logging
from datetime import datetime

from elasticsearch import Elasticsearch


class ElasticsearchHandler(logging.Handler):
    def __init__(self, es: Elasticsearch, application_name: str):
        super().__init__()
        self.application_name = application_name
        self.es = es

    def emit(self, record):
        date = datetime.utcnow()
        index = f"logstash-{date.strftime('%Y.%m.%d')}"
        log_data = {
            "@timestamp": date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            "level": record.levelname,
            "ApplicationName": self.application_name,
            "message": record.getMessage(),

        }
        self.es.index(index=index, body=log_data)
