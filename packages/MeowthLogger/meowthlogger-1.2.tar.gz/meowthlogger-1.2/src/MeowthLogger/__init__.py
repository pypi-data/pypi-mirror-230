import logging
import logging.config

class LoggerConfig:
    def __init__(self, filename="logging.log", logger_level="INFO", encoding="utf-8"):
        self.config = {
            'version': 1,
            'formatters': {
                'default': {
                    '()': 'MeowthLogger.Formatters.Default'
                },
                'colorised': {
                    '()': 'MeowthLogger.Formatters.Colorised'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': logger_level,
                    'formatter': 'colorised',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'MeowthLogger.Handlers.CustomHandler',
                    'level': logger_level,
                    'formatter': 'default',
                    'filename': filename,
                    'when': 'midnight',
                    'encoding': encoding
                }
            },
            'loggers': {
                'console': {
                    'level': logger_level,
                    'handlers': ['console'],
                    'propagate': False
                },
                'file': {
                    'level': logger_level,
                    'handlers': ['file'],
                    'propagate': False
                }
            },
            'root': {
                'level': logger_level,
                'handlers': ['console', 'file']
            }
        }

    @property
    def dict(self):
        return self.config


def initLogger(filename="logging.log", logger_level="INFO", encoding="utf-8"):
    config = LoggerConfig(filename, logger_level, encoding).dict
    logging.config.dictConfig(config)
