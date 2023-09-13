# Utils to load env variables and set up logging
from dotenv import load_dotenv #used locally in files
import logging
import yaml
import os
import sys
# Imports the Cloud Logging client library
import google.cloud.logging

from google.cloud.logging.handlers import CloudLoggingHandler

# print("\n******************\n\nTURNS OUT -E WORKED FOR PIP INSTALL!!!\n\n******************")
LOG_FORMAT = "%(levelname)s [function: %(funcName)s] - %(message)s"
ENV_FULL_PATH_IF_NULL = "/Users/croft/VScode/ptagit/env_vars.yaml"

# Check if code is running in VS Code debugger locally. If so, set TESTING_FLAG to empty string "" and don't exclude my slack id
os.environ["TESTING_FLAG"] = ""
if sys.gettrace() is not None:
    TESTING_FLAG = "True" #env variables are strings!
    # set testingflag as an env variable
    os.environ["TESTING_FLAG"] = str(TESTING_FLAG)
    print("\n******************\n\nRUNNING IN VS CODE DEBUGGER\n\n****************** (UTILS_INIT.PY)")
    EXCLUDED_SLACK_IDS = []


class CustomCloudLoggingHandler(CloudLoggingHandler):
    def _get_trace_and_span(self, record):
        trace, span = super()._get_trace_and_span(record)
        #if record.levelname == 'INFO':
        #    record.levelname = 'DEFAULT'
        return trace, span


def setup_new_logging(logger_name, log_level=logging.INFO, log_format=LOG_FORMAT):
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # Conditionally add console handler if not in production
    if os.getenv("TESTING_FLAG"):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    client = google.cloud.logging.Client()
    handler = CustomCloudLoggingHandler(client, name=logger_name)
    logger.addHandler(handler)

    logger.info(f"logger name: {logger_name}")

    return logger


# def setup_new_logging(logger_name, log_level=logging.INFO, log_format=LOG_FORMAT):
#     logger = logging.getLogger(logger_name)
#     logger.setLevel(log_level)
#     # Conditionally add console handler if not in production
#     if os.getenv("TESTING_FLAG"):
#         console_handler = logging.StreamHandler()
#         console_handler.setLevel(log_level)
#         formatter = logging.Formatter(log_format)
#         console_handler.setFormatter(formatter)
#         logger.addHandler(console_handler)

#     client = google.cloud.logging.Client()
#     client.setup_logging()
#     logger.info(f"logger name: {logger_name}")

#     return logger


def setup_logger(logger_name, log_level=logging.INFO, log_format=LOG_FORMAT):
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # only do google code and add console handler if running standalone
    if logger_name == '__main__' and not logger.handlers and os.getenv("TESTING_FLAG"):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)  # Set the log level on the handler
        formatter = logging.Formatter(log_format)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        # print(f"Adding handler to logger: {logger_name}")
    
        # Instantiates a client
        client = google.cloud.logging.Client()

        # Retrieves a Cloud Logging handler based on the environment you're running in and integrates the handler with the Python logging module. 
        client.setup_logging()
        logger.warning(f"Using OLD setup_logger call: {logger_name}")

    return logger


def load_env_variables_from_yaml(full_path_file_name=ENV_FULL_PATH_IF_NULL):    
    if hasattr(load_env_variables_from_yaml, "has_run"):
        return
    try:
        with open(full_path_file_name, 'r') as stream:
            params = yaml.safe_load(stream)
            for key, value in params.items():
                value = str(value) 
                os.environ[key] = value
        # set this attribute so don't keep running the function in the same program
        load_env_variables_from_yaml.has_run = True
    except FileNotFoundError:
        pass  # Ignore the file not found error as it is expected in some environments
            


# SCRAP:

    # Instantiates a client
    # client = google.cloud.logging.Client()

    # Retrieves a Cloud Logging handler based on the environment
    # you're running in and integrates the handler with the
    # Python logging module. By default this captures all logs
    # at INFO level and higher
    # client.setup_logging()

## COULD MAYBE DELETE SINCE SINCE LOAD_DOTENV SHOWS UP AS A METHOD WITH MORE OPTIONS WHEN USING THIS UTILS_INIT!!!
# def DELETE_load_dotenv_file(path = "../.env"):
    # load_dotenv(dotenv_path=path)
