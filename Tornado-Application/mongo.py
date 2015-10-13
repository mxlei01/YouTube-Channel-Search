import motor
import mongo_settings
import exceptions
import tornado.ioloop
import logger
from tornado import gen
from pymongo import errors
from bson.code import Code

# mongo.py includes all the methods to access mongo db, and settings

# setup a mongodb client
client = motor.MotorClient(mongo_settings.mongodb_address, mongo_settings.mongodb_port)

# reducer code to append all the values aggregated into a stringified version of
# an array, since map reduce in mongodb cannot return an array
reducer = Code("""
                function (key, values) {
                  var total = [];
                  for (var i = 0; i < values.length; i++) {
                    total.push(values[i]);
                  }
                  return total.toString();
                }
                """)

# mapper code to map username to videoId, note that there can be multiple videoId
# hence we need to use the reducer to reduce the multiple videoId's to a single username
mapper = Code("""
               function () {
			emit (this.username, this.videoId);
                 };
               """)

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
def insert_user_video_comments(db_client, commentId, channelName, username, textDisplay, dateOfReply, channelId, videoId, title, description, dateOfVideo):
    # Usage:
    #       Inserts a user comment into mongodb
    # Arguments:
    #       db_client      : the client of mongodb
    #       commentId      : the comment ID of a comment
    #       channelName    : the channel name, which is not the channel ID
    #       username       : username who commented
    #       textDisplay    : the comment that the user posted
    #       dateOfReply    : when the date was posted
    #       channelId      : the channel ID of a channel
    #       videoId        : the video ID of a video
    #       title          : title of a video
    #       description    : description of a video
    #       dateOfVideo    : date of the video uploaded
    # Return:
    #       result of the insertion

    # Get the collection: comments, from database: youtube
    collection = db_client.youtube.comments

    # Create a document from videoId, title, and description
    # using channelId, and videoId as a primary key
    document = {"_id":commentId, "channelName":channelName, "username":username, "textDisplay":textDisplay, "dateOfReply":dateOfReply,
                "channelId":channelId, "videoId":videoId, "title":title, "description":description, "dateOfVideo":dateOfVideo}

    # Yields the insertion of the video, and tries to insert, which can fail
    # since there might be already a videoId
    result = None
    try:
        result = yield collection.insert(document)
    except errors.DuplicateKeyError:
        pass

    raise gen.Return(result)

@gen.coroutine
def aggregate_user_videoId(db_client, mapper, reducer, resultName, queryKey, queryValue):
    # Usage:
    #       Outputs a aggregation for user and videoId
    # Arguments:
    #       db_client      : the client of mongodb
    #       mapper         : mapper code in javascript
    #       reducer        : reducer code in javascript
    #       resultName     : a collection name to be stored inside mongoDB
    #       queryKey       : the key we are querying, can be channelID or channelName
    #       queryValue     : the value we are querying
    # Return:
    #       a collection of aggregation between user and videoId

    # Get the collection: comments, from database: youtube
    collection = db_client.youtube.comments

    # Performs a mapreduce on the given mapper, and reducer code
    # and does a query on the query value so that we can filter out other
    # channel data
    result = yield collection.map_reduce(mapper, reducer, resultName, query={queryKey:queryValue})

    # Returns the collection back
    raise gen.Return(result)

@gen.coroutine
def insert_aggregate_user_video(db_client, userVideos, comment):
    # Usage:
    #       Inserts a key as a username, and an key of channelId mapped to videoId and videoName
    # Arguments:
    #       db_client      : the client of mongodb
    #       userVideos     : the user videos row, where user is a username, and row is
    #                        a comma seperated list of videos that a user commented on
    #       comment        : comment from the user
    # Return:
    #       result of the insertion

    # Get the collection: comments, from database: youtube
    collection = db_client.youtube.user_video

    # Yields the insertion of the a user comment, and appends new video comments into the
    # channelId array if has not existed yet
    result = None
    try:
        result = yield collection.update({"_id":userVideos["_id"]},
                                         {"$addToSet":{comment["channelId"]:{"comment":comment["textDisplay"],
                                                                             "videoName":comment["title"],
                                                                             "time":comment["dateOfReply"]}}}, True)
    except errors.DuplicateKeyError:
        pass

    raise gen.Return(result)