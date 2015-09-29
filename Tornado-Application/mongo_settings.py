# Import pymongo
import pymongo
# Import tornado libraries
from tornado import gen

# db_settings.py includes the mongodb's settings

# defines the mongodb address that we are going to connect
mongodb_address = 'localhost'

# defines the moongodb port that we are going to connect
mongodb_port = 27017

@gen.coroutine
def createIndexesAtWithDirection(collection, field, direction):
    # Usage:
    #       creates indexes on a collection on date and descending
    # Arguments:
    #       collection  : Used for creation of indexes in the collection of the a specific database
    # Return:
    #       None

    # Creates an index at date in descending
    yield collection.create_index(field, direction)

@gen.coroutine
def createIndexAt(collection, variable):
    # Usage:
    #       creates indexes on a collection on on a variable
    # Arguments:
    #       collection  : Used for creation of indexes in the collection of the a specific database
    # Return:
    #       None

    # Creates an index at date in descending
    yield collection.create_index(variable)

def createIndexes(client):
    # Usage:
    #       Creates indexes on fields on the youtube database, with three
    #       different tables, such as videos, user, comments, which are used
    #       to speedup queries for sorting, and uniqueness on user and date.
    # Arguments:
    #       client: MongoDB Client
    # Return:
    #       None

    # Create indexes on video and user and on date in descending
    createIndexesAtWithDirection(client.youtube.video, "date", pymongo.DESCENDING)
    createIndexesAtWithDirection(client.youtube.user, "date", pymongo.DESCENDING)
    # Create indexes on username, so that queries on user is faster
    createIndexAt(client.youtube.user, "username")
    # Create indexes on username and date, so that queries on the user is faster
    createIndexAt(client.youtube.comments, "username")
    createIndexesAtWithDirection(client.youtube.comments, "dateOfReply", pymongo.DESCENDING)
    createIndexesAtWithDirection(client.youtube.comments, "dateOfVideo", pymongo.DESCENDING)
    # Create indexes on videoId and channelId, since we will need to find distinct, or query against them
    createIndexAt(client.youtube.comments, "channelId")
    createIndexAt(client.youtube.comments, "videoId")