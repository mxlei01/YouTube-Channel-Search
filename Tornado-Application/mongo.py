# Import motor libraries
import motor
# Import mongodb settings
import mongo_settings
# Import exceptions
import exceptions
import tornado.ioloop
# Import logger
import logger

# mongo.py includes all the methods to access mongo db

# setup a mongodb client
client = motor.MotorClient(mongo_settings.mongodb_address, mongo_settings.mongodb_port)

def checkMongoDB(*args):
    # Usage:
    #       Tests whether if the
    # Arguments:
    #       None
    # Return:
    #       None

    # Check if the first argument is false, that means we cannot connect
    if not args[0]:

        # If we cannot connect to mongoDB, we will get the current ioloop, and stop it
        tornado.ioloop.IOLoop.current().stop()

        # Raise an exceptions to the user
        logger.logger.info("Cannot connect to MongoDB on address:" + str(mongo_settings.mongodb_address) + ", port:" + str(mongo_settings.mongodb_port))

        # Raise an IO exceptions to the user that we cannot connect to MongoDB
        raise exceptions.IOError("Cannot connect to MongoDB")
    else:

        # Log the user on successful connection attempt
        logger.logger.info("Connected to MongoDB on address:" + str(mongo_settings.mongodb_address) + ", port:" + str(mongo_settings.mongodb_port))
