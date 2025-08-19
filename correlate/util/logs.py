
import logging
import sys

# Obtain the root logger.
logger = logging.getLogger()

# Set the logging level to 'logging.INFO' by default.
logger.setLevel(logging.INFO)

# Set @logger to write logs to stdout (console).
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

# Create the formatter for the log messages.
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# Set the formatter for the handler.
handler.setFormatter(formatter)

# Use the stdout log handler for the root logger.
logger.addHandler(handler)
