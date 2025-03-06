import logging
import os
import pika
from configparser import ConfigParser

def get_caller(script_name):
    """Extract the calling script name"""
    return os.path.splitext(os.path.basename(script_name))[0]


def setup_logging(config):
    log_file = config.get('DEFAULT', 'log_file')
    # Get the log level from the config
    app_log_level_str = config.get('DEFAULT', 'app_log_level', fallback='INFO') #Added fallback, in case the key does not exist.

    # Convert the string log level to a logging level attribute
    try:
        app_log_level = getattr(logging, app_log_level_str.upper(), logging.INFO)
    except AttributeError:
        print(f"Invalid log level '{app_log_level_str}' in config. Using INFO.")
        app_log_level = logging.INFO

    logging.basicConfig(filename=log_file, level=app_log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Get the root logger for the pika package
    pika_logger = logging.getLogger('pika')
    rabbit_log_level_str = config.get('DEFAULT', 'rabbit_log_level', fallback='INFO') #Added fallback, in case the key does not exist.

    # Set the logging level to WARNING
    pika_logger.setLevel(rabbit_log_level_str)

def log_info(message, logger):
    logger.info(message)

def log_exception(message, logger):
    logger.exception(message)

def log_error(message, logger):
    logger.error(message)

def load_config(config, section_name, logger):
    """Loads configuration from the config object based on the parameter section_name"""
    key_config = {}  # Dictionary to store the configuration

    if config.has_section(section_name):              # Check if the section exists
        for key, value in config.items(section_name): # Iterate over the options in the section
            key_config[key] = value                   # Store each option in the dictionary
        logger.info(f"Loading configuration for {section_name}: success")
    else:
        logger.info(f"Loading configuration for {section_name}: error")

    return key_config


def get_config():
    config = ConfigParser()

    config_file_paths = [
        "config.ini",                                                # Try current directory first
        os.path.join(os.path.dirname(__file__), "..", "config.ini"), # Try parent directory
        "/etc/myapp/config.ini",                                     # Try system-wide config directory
    ]

    for path in config_file_paths:
        if os.path.exists(path):
            config.read(path)
            break # Stop searching after finding the file

    if not config.sections():
        raise FileNotFoundError("config.ini not found")

    return config

def nvl(value, default_value):
    """Returns default_value if value is None, otherwise returns value."""
    return default_value if value is None else value
