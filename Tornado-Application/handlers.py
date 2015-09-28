# Import tornado libraries
import tornado.web
from tornado import gen
# Import concurrent libraries
from concurrent import futures
# Import coroutines functions
import coroutines
# Import synchronous functions
import synchronous
# Import executurs for synchronous tasks
import executors
# Import youtube api
import youtube_api
# Import settings, so that we can get our youtube api key
import settings
# Import logging
import logger
# Import mongo functions
import mongo

# handlers.py contains all the handlers that tornado application uses

class TestRequestHandler(tornado.web.RequestHandler):
    # Test handler is mapped to / in url.py
    # to test, simply type localhost:8888/ in the web browser

    def get(self):
        # Usage:
        #       Get request, used to test if the tornado application is responding
        #       i.e. localhost:8888/
        # Arguments:
        #       None
        # Return:
        #       None

        self.write("Hello, world")

class ChannelRequestHandler(tornado.web.RequestHandler):
    # Handler to receive channel names from the meteor js application

    def initialize(self, db):
        # Usage:
        #       constructor for the request handler, this will attach the mongodb client
        #       to the request handler
        # Arguments:
        #       None
        # Return:
        #       None

        self.db = db

    @gen.coroutine
    def get(self):
        # Usage:
        #       Get request, we will use youtube's api to get the channel information
        #       which include channel information, videos, and user comments, and add the
        #       data into mongodb
        #       i.e. localhost:8888/
        # Arguments:
        #       None
        # Return:
        #       None

        # Get channel name
        channelName = self.get_argument('id')

        # A flag to indicate if we have more channels to search for
        channelNextPageToken = True

        # Build the first channelNameAPI string
        getChannelAPI = youtube_api.getChannels % (channelName, settings.youtube_API_key, "")

        print "Start"

        # Loop through channels if nextPageToken exists
        while channelNextPageToken:
            # Fetch the data for the channel
            channelNameJson = yield coroutines.fetch_coroutine(getChannelAPI)
            logger.logger.info("channelName:%s, getChannelAPI:%s, channelNameJson:%s" % (channelName, getChannelAPI, channelNameJson))

            # Loop through each channel ID inside the json array with the key items
            for channelID in channelNameJson["items"]:
                # Create a getVideos api string
                getVideosAPI = youtube_api.getVideos % (channelID["id"], settings.youtube_API_key, "")

                # A flag to indicate that we have more pages to search for
                videosNextPageToken = True

                # Loop through videos if nextPageToken exists
                while videosNextPageToken:
                    # Fetch the data for videos
                    videosJson = yield coroutines.fetch_coroutine(getVideosAPI)
                    logger.logger.info("getVideosAPI:%s, videosJson:%s" % (getVideosAPI, videosJson))

                    # Loop through each videos
                    for video in videosJson["items"]:
                        # Create a getCommentThread api string
                        getCommentThreadAPI = youtube_api.getCommentThread % (video["id"]["videoId"], settings.youtube_API_key, "")

                        # A flag to indicate that we have more comments to go through
                        commentThreadNextPageToken = True

                        # Store the information of the video inside the video collection
                        result = yield mongo.insert_video(self.db, channelID["id"], video["id"]["videoId"], video["snippet"]["title"], video["snippet"]["description"], video["snippet"]["publishedAt"])
                        logger.logger.info("mongo.insert_video, channelID[id]:%s, video[id][videoId]:%s, video[snippet][title]:%s, video[snippet][description]:%s, video[snippet][publishedAt]:%s, result:%s"
                                           % (channelID["id"], video["id"]["videoId"], video["snippet"]["title"], video["snippet"]["description"], video["snippet"]["publishedAt"], result))

                        # Loop through next set of comments
                        while commentThreadNextPageToken:
                            # Fetch the comments for a specific video
                            commentThreadJson = yield coroutines.fetch_coroutine(getCommentThreadAPI)
                            logger.logger.info("getCommentThreadAPI:%s, commentThreadJson:%s" % (getCommentThreadAPI, commentThreadJson))

                            # Loop through each top level comments
                            for topComment in commentThreadJson["items"]:
                                # Store the Data into MongoDB
                                result = yield mongo.insert_user_comments(self.db, video["id"]["videoId"], topComment["id"], topComment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"], topComment["snippet"]["topLevelComment"]["snippet"]["textDisplay"], topComment["snippet"]["topLevelComment"]["snippet"]["updatedAt"])
                                logger.logger.info("mongo.insert_user_comments, video[id][videoId]:%s, topComment[id]:%s, topComment[snippet][topLevelComment][snippet][authorDisplayName]:%s, topComment[snippet][topLevelComment][snippet][textDisplay]:%s, topComment[snippet][topLevelComment][snippet][updatedAt]:%s, result:%s"
                                                   % (video["id"]["videoId"], topComment["id"], topComment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"], topComment["snippet"]["topLevelComment"]["snippet"]["textDisplay"], topComment["snippet"]["topLevelComment"]["snippet"]["updatedAt"], result))

                                # If the total reply count > 0, then we know that there are replies
                                # to this comment
                                if topComment["snippet"]["totalReplyCount"] > 0:
                                    # Create a getCommentReplies api string
                                    getCommentRepliesAPI = youtube_api.getCommentReplies % (topComment["id"], settings.youtube_API_key, "")

                                    # A flag to indicate that we have more replies to go through
                                    commentRepliesNextPageToken = True

                                    # Loop through each set of replies
                                    while commentRepliesNextPageToken:
                                        # Fetch the replies for a specific comment
                                        commentRepliesJson = yield coroutines.fetch_coroutine(getCommentRepliesAPI)
                                        logger.logger.info("getCommentRepliesAPI:%s, commentRepliesJson:%s" % (getCommentRepliesAPI, commentRepliesJson))

                                        # Loop through each top comment replies
                                        for replies in commentRepliesJson["items"]:
                                            # Store the data into MongoDB
                                            result = yield mongo.insert_user_comments(self.db, video["id"]["videoId"], replies["id"], replies["snippet"]["authorDisplayName"], replies["snippet"]["textDisplay"], replies["snippet"]["updatedAt"])
                                            logger.logger.info("mongo.insert_user_comments_replies, video[id][videoId]:%s, topComment[id]:%s, topComment[snippet][authorDisplayName]:%s, topComment[snippet][textDisplay]:%s, topComment[snippet][updatedAt]:%s, result:%s"
                                                               % (video["id"]["videoId"], replies["id"], replies["snippet"]["authorDisplayName"], replies["snippet"]["textDisplay"], replies["snippet"]["updatedAt"], result))

                                        # If next page token does not exist, then we can stop the loop
                                        if "nextPageToken" not in commentRepliesJson:
                                            # If the nextPageToken does not exist, then we can end the while loop
                                            commentRepliesNextPageToken = False
                                        else:
                                            # If it does exist, then we build the getVideosAPI with the next page token to go the next set of videos
                                            getCommentRepliesAPI = youtube_api.getCommentReplies % (topComment["id"], settings.youtube_API_key, commentRepliesJson["nextPageToken"])

                            # If next page token does not exist, then we can stop the loop
                            if "nextPageToken" not in commentThreadJson:
                                # If the nextPageToken does not exist, then we can end the while loop
                                commentThreadNextPageToken = False
                            else:
                                # If it does exist, then we build the getVideosAPI with the next page token to go the next set of videos
                                getCommentThreadAPI = youtube_api.getCommentThread % (video["id"]["videoId"], settings.youtube_API_key, commentThreadJson["nextPageToken"])

                    # If next page token does not exist, then we can stop the loop
                    if "nextPageToken" not in videosJson:
                        # If the nextPageToken does not exist, then we can end the while loop
                        videosNextPageToken = False
                    else:
                        # If it does exist, then we build the getVideosAPI with the next page token to go the next set of videos
                        getVideosAPI = youtube_api.getVideos % (channelID["id"], settings.youtube_API_key, videosJson["nextPageToken"])

            # If next page token does not exist, then we can stop the loop
            if "nextPageToken" not in channelNameJson:
                # If the nextPageToken does not exist, then we can end the while loop
                channelNextPageToken = False
            else:
                # If it does exist, then we build the getChannelAPI with the next page token, we can go to the next set of channels
                getChannelAPI = youtube_api.getChannels % (channelName, settings.youtube_API_key, channelNameJson["nextPageToken"])

        print "End"

        #response = { 'status': 'done' }
        #self.write(response)

        self.write("Done")