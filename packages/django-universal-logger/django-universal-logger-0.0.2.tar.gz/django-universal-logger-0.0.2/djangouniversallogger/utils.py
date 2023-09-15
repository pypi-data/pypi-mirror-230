import os

from django.conf import settings


def load_from_settings(var_name, default):
    return getattr(settings, var_name, default)


def load_logs_dir():
    logs_dir = load_from_settings('LOGS_DIR', os.path.join(settings.BASE_DIR, 'logs'))
    return logs_dir


def load_check_logger():
    return load_from_settings('CHECK_LOGGER', True)
