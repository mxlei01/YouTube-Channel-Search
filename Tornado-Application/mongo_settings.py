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
def createIndexesDateDescending(collection):
    # Usage:
    #       creates indexes on a collection on date and descending
    # Arguments:
    #       collection  : Used for creation of indexes in the collection of the a specific database
    # Return:
    #       None

    # Creates an index at date in descending
    yield collection.create_index("date", pymongo.DESCENDING)

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