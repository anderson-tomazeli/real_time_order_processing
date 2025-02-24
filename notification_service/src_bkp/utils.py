import logging
import os
from configparser import ConfigParser

def setup_logging(config):
    log_file = config.get('DEFAULT', 'log_file')
    log_level = config.get('DEFAULT', 'log_level')

    # Create the logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(filename=log_file, level=log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    return logging.getLogger(__name__)  # Return a logger instance

def load_config(config, section_name):
    """Loads configuration from the config object based on the parameter section_name"""
    logger = setup_logging(config)

    key_config = {}  # Dictionary to store the configuration

    if config.has_section(section_name):              # Check if the section exists
        for key, value in config.items(section_name): # Iterate over the options in the section
            key_config[key] = value                   # Store each option in the dictionary
        logger.info(f"Loading configuration for {section_name}: success")
    else:
        #raise ValueError("{section_name} section not found in config file.")
        #logger.exception(f"{section_name} section not found in config file.")
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

# Other utility functions can go here...
