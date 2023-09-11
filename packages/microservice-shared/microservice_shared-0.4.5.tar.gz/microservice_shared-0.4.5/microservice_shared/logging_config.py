"""
Log config functions
"""
from typing import Dict, Any


# Define constants for clarity
MEGABYTE = 1024 * 1024
TEN_MEGABYTES = 10 * MEGABYTE
BACKUP_COUNT = 5


def get_logging_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a logging configuration based on the provided config.

    Args:
        config (Dict[str, Any]): Configuration dictionary.

    Returns:
        Dict[str, Any]: Logging configuration dictionary.
    """

    log_dir = config("LOG_DIR")
    application_logger_name = config("APPLICATION_LOGGER_NAME")

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": (
                    "{asctime} [{levelname}] {name} {module}.{funcName} "
                    "({process:d}) {thread:d} {pathname}:{lineno:d} - {message}"
                ),
                "style": "{",
            }
        },
        "handlers": {
            "access_debug_log": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/access_log/debug.log",
                "maxBytes": TEN_MEGABYTES,
                "backupCount": BACKUP_COUNT,
                "formatter": "verbose",
            },
            "access_info_log": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/access_log/info.log",
                "maxBytes": TEN_MEGABYTES,
                "backupCount": BACKUP_COUNT,
                "formatter": "verbose",
            },
            "access_warning_log": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/access_log/warning.log",
                "maxBytes": TEN_MEGABYTES,
                "backupCount": BACKUP_COUNT,
                "formatter": "verbose",
            },
            "access_error_log": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/access_log/error.log",
                "maxBytes": TEN_MEGABYTES,
                "backupCount": BACKUP_COUNT,
                "formatter": "verbose",
            },
            "application_debug_log": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/application_log/debug.log",
                "maxBytes": TEN_MEGABYTES,
                "backupCount": BACKUP_COUNT,
                "formatter": "verbose",
            },
            "application_info_log": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/application_log/info.log",
                "maxBytes": TEN_MEGABYTES,
                "backupCount": BACKUP_COUNT,
                "formatter": "verbose",
            },
            "application_warning_log": {
                "level": "WARNING",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/application_log/warning.log",
                "maxBytes": TEN_MEGABYTES,
                "backupCount": BACKUP_COUNT,
                "formatter": "verbose",
            },
            "application_error_log": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/application_log/error.log",
                "maxBytes": TEN_MEGABYTES,
                "backupCount": BACKUP_COUNT,
                "formatter": "verbose",
            },
            "application_critical_log": {
                "level": "CRITICAL",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{log_dir}/application_log/critical.log",
                "maxBytes": TEN_MEGABYTES,
                "backupCount": BACKUP_COUNT,
                "formatter": "verbose",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "loggers": {
            "django": {
                "handlers": [
                    "access_debug_log",
                    "access_info_log",
                    "access_warning_log",
                    "access_error_log",
                ],
                "level": "DEBUG",
                "propagate": False,
            },
            application_logger_name: {
                "handlers": [
                    "application_debug_log",
                    "application_info_log",
                    "application_warning_log",
                    "application_error_log",
                    "application_critical_log",
                    "console",
                ],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }
