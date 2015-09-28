# Import motor libraries
import motor
# Import mongodb settings
import mongo_settings
# Import exceptions
import exceptions
import tornado.ioloop
# Import logger
import logger
# Import tornado libraries
from tornado import gen
# Import pymongo exceptions
from pymongo import errors
# Import pymongo
import pymongo

# mongo.py includes all the methods to access mongo db, and settings

# setup a mongodb client
client = motor.MotorClient(mongo_settings.mongodb_address, mongo_settings.mongodb_port)

def checkMongoDB(*args):
    # Usage:
    #       Tests whether if the the mongodb server is alive
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

@gen.coroutine
def insert_video(db_client, channelId, videoId, title, description, date):
    # Usage:
    #       Inserts a video into mongodb
    # Arguments:
    #       db_client   : the client of mongodb
    #       channelID   : the channel ID of a channel
    #       videoId     : the video ID of a video
    #       title       : title of a video
    #       description : description of a video
    #       date        : date of the video uploaded
    # Return:
    #       None

    # Get the collection: video, from database: youtube
    collection = db_client.youtube.video

    # Create a document from videoId, title, and description
    # using channelId, and videoId as a primary key
    document = {"_id":{"channelId":channelId, "videoId":videoId}, "title":title, "description":description, "date":date}

    # Yields the insertion of the video, and tries to insert, which can fail
    # since there might be already a videoId
    result = None
    try:
        result = yield collection.insert(document)
    except errors.DuplicateKeyError:
        pass

    raise gen.Return(result)

@gen.coroutine
def insert_user_comments(db_client, videoId, commentId, username, textDisplay, date):
    # Usage:
    #       Inserts a user comment into mongodb
    # Arguments:
    #       db_client   : the client of mongodb
    #       commentId   : the comment ID of a comment
    #       username    : username who commented
    #       textDisplay : the comment that the user posted
    #       date        : when the date was posted
    # Return:
    #       None

    # Get the collection: user, from database: youtube
    collection = db_client.youtube.user

    # Create a document from videoId, title, and description
    # using channelId, and videoId as a primary key
    document = {"_id":{"videoId":videoId, "commentId":commentId}, "username":username, "textDisplay":textDisplay, "date":date}

    # Yields the insertion of the video, and tries to insert, which can fail
    # since there might be already a videoId
    result = None
    try:
        result = yield collection.insert(document)
    except errors.DuplicateKeyError:
        pass

    raise gen.Return(result)
