# Import tornado libraries
import tornado
import tornado.ioloop
import tornado.web
# Import mongodb client
import mongo
import mongo_settings
# Import URL mappings
from url import application
# Import logger
import logger
# Import tornado settings
import settings

# main.py is the main access point of the tornado app, to run the application, just run "python main.py"

# What this will do is listen to port in the settings.py file, and then we can access the app using
# http://localhost:settings.port on any browser, or using python requests library
if __name__ == "__main__":
    # Check if mongoDB is available
    mongo.client.admin.command('ping', callback=mongo.checkMongoDB)

    # Create neccessary indexes on video and user and on date in descending
    mongo_settings.createIndexesDateDescending(mongo.client.youtube.video)
    mongo_settings.createIndexesDateDescending(mongo.client.youtube.user)

    # Set the application to listen to port 8888
    application.listen(settings.port)

    # Get the current IOLoop
    currentIOLoop = tornado.ioloop.IOLoop.current()

    # Log the port that is listened
    logger.logger.info("Started application on port:" + str(settings.port))

    # Start the IOLoop
    currentIOLoop.start()