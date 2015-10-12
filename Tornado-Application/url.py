# Import tornado libraries
import tornado.web
# Import handlers and settings
from handlers import ChannelRequestHandler
from settings import settings
# Import mongodb client for request handlers
import mongo

# url.py is used to map between different urls to handlers, and also to set different settings

# application is a tornado web application object, that can be used to set handlers, and settings
application = tornado.web.Application([
    # Map the "/" url to main handler
    (r"/channel", ChannelRequestHandler, dict(db=mongo.client))
], **settings)