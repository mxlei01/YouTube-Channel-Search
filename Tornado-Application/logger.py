import logging
import logging.handlers

# logger.py is used to setup loggin support in a file

def setupLogger():
    # Usage:
    #       Sets up the logger, based on the module name: __name__
    # Arguments:
    #       None
    # Return:
    #       None

    # Get a logger based on loggerName
    logger = logging.getLogger(__name__)

    # Set the level to INFO, so everything gets logged at INFO level
    logger.setLevel(logging.INFO)

    # Create a Rotating File Handler with the loggerFileName
    handler = logging.handlers.RotatingFileHandler(__name__+".log", maxBytes=2000000, backupCount=5)

    # Create a formatter so the outputs would have name, time, level, and message
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(thread)d - %(threadName)s - %(levelname)s - %(message)s')

    # Set the formatter to the handler
    handler.setFormatter(formatter)

    # Set the handler to the logger
    logger.addHandler(handler)

    # Return the logger, so that we can use it later
    return logger

# setups up a logger using setupLogger
logger = setupLogger()