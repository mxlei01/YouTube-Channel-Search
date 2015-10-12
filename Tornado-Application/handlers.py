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
import mongo, mongo_settings

# handlers.py contains all the handlers that tornado application uses

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

    def getChannelAPI(self, channelName, channelID):
        # Usage:
        #       Since only channelName or channelID is populated, we will test
        #       if channelName or channelID exists. If channelName exists, then
        #       we will use youtube_api.getChannelAPI, else youtube_api.getChannels_withID
        # Arguments:
        #       channelName: name of a channel
        #       channelID  : ID of a channel
        # Return:
        #       channelAPI : the API we are using to get our channel information

        channelAPI = None

        if channelID:
            channelAPI = youtube_api.getChannels_withID % (channelID, settings.youtube_API_key, "")
        else:
            channelAPI = youtube_api.getChannels % (channelName, settings.youtube_API_key, "")

        return channelAPI

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

        # Get channel name and channel ID (one of them are empty)
        channelName = self.get_argument('name')
        channelID = self.get_argument('id')

        # Determine the API that we are going to use, whether it is primary channelName or channelID
        getChannelAPI = self.getChannelAPI(channelName, channelID)

        # A flag to indicate if we have more channels to search for
        channelNextPageToken = True

        # Loop through channels if nextPageToken exists
        while channelNextPageToken:
            # Fetch the data for the channel
            channelNameJson = yield coroutines.fetch_coroutine(getChannelAPI)
            logger.logger.info("channelName:%s, channelID:%s, getChannelAPI:%s, channelNameJson:%s" % (channelName, channelID, getChannelAPI, channelNameJson))

            # Sometimes a fetch can fail, and return None
            if channelNameJson:
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

                        # Sometimes a fetch can fail, and return None
                        if videosJson:
                            # Loop through each videos
                            for video in videosJson["items"]:
                                # Check if it is actually a video, because sometimes if the channel/user subscribed to a channel
                                # it will also appear in this place too
                                if "videoId" in video["id"]:
                                    # Create a getCommentThread api string
                                    getCommentThreadAPI = youtube_api.getCommentThread % (video["id"]["videoId"], settings.youtube_API_key, "")

                                    # A flag to indicate that we have more comments to go through
                                    commentThreadNextPageToken = True

                                    # Store the information of the video inside the video collection
                                    # Disabled since meteor cannot use composite keys
                                    #result = yield mongo.insert_video(self.db, channelID["id"], video["id"]["videoId"], video["snippet"]["title"], video["snippet"]["description"], video["snippet"]["publishedAt"])
                                    #logger.logger.info("mongo.insert_video, channelID[id]:%s, video[id][videoId]:%s, video[snippet][title]:%s, video[snippet][description]:%s, video[snippet][publishedAt]:%s, result:%s"
                                    #                   % (channelID["id"], video["id"]["videoId"], video["snippet"]["title"], video["snippet"]["description"], video["snippet"]["publishedAt"], result))

                                    # Loop through next set of comments
                                    while commentThreadNextPageToken:
                                        # Fetch the comments for a specific video
                                        commentThreadJson = yield coroutines.fetch_coroutine(getCommentThreadAPI)
                                        logger.logger.info("getCommentThreadAPI:%s, commentThreadJson:%s" % (getCommentThreadAPI, commentThreadJson))

                                        # Sometimes a fetch can fail, and return None
                                        if commentThreadJson:
                                            # Loop through each top level comments
                                            for topComment in commentThreadJson["items"]:
                                                # Store the Data into MongoDB
                                                # Disabled since meteor cannot use composite keys
                                                #result = yield mongo.insert_user_comments(self.db, video["id"]["videoId"], topComment["id"], topComment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"], topComment["snippet"]["topLevelComment"]["snippet"]["textDisplay"], topComment["snippet"]["topLevelComment"]["snippet"]["updatedAt"])
                                                #logger.logger.info("mongo.insert_user_comments, video[id][videoId]:%s, topComment[id]:%s, topComment[snippet][topLevelComment][snippet][authorDisplayName]:%s, topComment[snippet][topLevelComment][snippet][textDisplay]:%s, topComment[snippet][topLevelComment][snippet][updatedAt]:%s, result:%s"
                                                #                   % (video["id"]["videoId"], topComment["id"], topComment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"], topComment["snippet"]["topLevelComment"]["snippet"]["textDisplay"], topComment["snippet"]["topLevelComment"]["snippet"]["updatedAt"], result))

                                                # Store the Data into MongoDB
                                                result = yield mongo.insert_user_video_comments(self.db, topComment["id"],
                                                                                                channelName,
                                                                                                topComment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                                                                                              topComment["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                                                                                                topComment["snippet"]["topLevelComment"]["snippet"]["updatedAt"],
                                                                                                channelID["id"],
                                                                                                video["id"]["videoId"],
                                                                                                video["snippet"]["title"],
                                                                                                video["snippet"]["description"],
                                                                                                video["snippet"]["publishedAt"])
                                                logger.logger.info("mongo.insert_user_video_comments, "
                                                                   "topComment[id]:%s, "
                                                                   "channelName:%s, "
                                                                   "topComment[snippet][topLevelComment][snippet][textDisplay]:%s, "
                                                                   "topComment[snippet][topLevelComment][snippet][authorDisplayName]:%s, "
                                                                   "topComment[snippet][topLevelComment][snippet][updatedAt]:%s, "
                                                                   "channelID[id]:%s, "
                                                                   "video[id][videoId]:%s, "
                                                                   "video[snippet][title]:%s, "
                                                                   "video[snippet][description]:%s, "
                                                                   "video[snippet][publishedAt]:%s, "
                                                                   "result:%s"
                                                                    % (topComment["id"],
                                                                        channelName,
                                                                        topComment["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                                                                        topComment["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                                                                        topComment["snippet"]["topLevelComment"]["snippet"]["updatedAt"],
                                                                        channelID["id"],
                                                                        video["id"]["videoId"],
                                                                        video["snippet"]["title"],
                                                                        video["snippet"]["description"],
                                                                        video["snippet"]["publishedAt"],result))


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

                                                        # Sometimes a fetch can fail, and return None
                                                        if commentRepliesJson:
                                                            # Loop through each top comment replies
                                                            for replies in commentRepliesJson["items"]:
                                                                # Store the data into MongoDB
                                                                # Disabled since meteor cannot use composite keys
                                                                #result = yield mongo.insert_user_comments(self.db, video["id"]["videoId"], replies["id"], replies["snippet"]["authorDisplayName"], replies["snippet"]["textDisplay"], replies["snippet"]["updatedAt"])
                                                                #logger.logger.info("mongo.insert_user_comments_replies, video[id][videoId]:%s, topComment[id]:%s, topComment[snippet][authorDisplayName]:%s, topComment[snippet][textDisplay]:%s, topComment[snippet][updatedAt]:%s, result:%s"
                                                                #                   % (video["id"]["videoId"], replies["id"], replies["snippet"]["authorDisplayName"], replies["snippet"]["textDisplay"], replies["snippet"]["updatedAt"], result))

                                                                # Store the data into MongoDB
                                                                result = yield mongo.insert_user_video_comments(self.db, replies["id"],
                                                                                                                channelName,
                                                                                                                replies["snippet"]["authorDisplayName"],
                                                                                                                replies["snippet"]["textDisplay"],
                                                                                                                replies["snippet"]["updatedAt"],
                                                                                                                channelID["id"],
                                                                                                                video["id"]["videoId"],
                                                                                                                video["snippet"]["title"],
                                                                                                                video["snippet"]["description"],
                                                                                                                video["snippet"]["publishedAt"])
                                                                logger.logger.info("mongo.insert_user_video_comments, "
                                                                                   "replies[id]:%s, "
                                                                                   "channelName:%s, "
                                                                                   "replies[snippet][authorDisplayName]:%s, "
                                                                                   "replies[snippet][textDisplay]:%s, "
                                                                                   "replies[snippet][updatedAt]:%s, "
                                                                                   "channelID[id]:%s, "
                                                                                   "video[id][videoId]:%s, "
                                                                                   "video[snippet][title]:%s, "
                                                                                   "video[snippet][description]:%s, "
                                                                                   "video[snippet][publishedAt]:%s, "
                                                                                   "result:%s"
                                                                                    % (replies["id"],
                                                                                        channelName,
                                                                                        replies["snippet"]["authorDisplayName"],
                                                                                        replies["snippet"]["textDisplay"],
                                                                                        replies["snippet"]["updatedAt"],
                                                                                        channelID["id"],
                                                                                        video["id"]["videoId"],
                                                                                        video["snippet"]["title"],
                                                                                        video["snippet"]["description"],
                                                                                        video["snippet"]["publishedAt"],result))


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
                    # Build the first channelNameAPI string
                    getChannelAPI = youtube_api.getChannels % (channelName, settings.youtube_API_key, channelNameJson["nextPageToken"])
                    # If there is channelID, then create it using channelID
                    if channelID:
                        getChannelAPI = youtube_api.getChannels_withID % (channelID, settings.youtube_API_key, channelNameJson["nextPageToken"])

        # Get the queryKey and queryResult depending on if the user has provided a
        # channelID.
        channelName = self.get_argument('name')
        channelID = self.get_argument('id')
        queryKey = "channelName"
        queryResult = channelName
        if channelID:
            queryKey = "channelId"
            queryResult = channelID

        # The next part of the task is to aggregate the data, where we want to get all the videos
        # in a specific channel that matches to a username
        # _id:Username
        # 	{Video1, channelID}
        #		Comments
        #		Comments
        #	{Video1, channelID}
        #		Comments
        #		Comments
        #	{Video1, channelID}
        #		Comments
        result = yield mongo.aggregate_user_videoId(mongo.client, mongo.mapper, mongo.reducer, mongo_settings.tempCollectionName, queryKey, queryResult)
        logger.logger.info("aggregate_user_videoId, mongo.mapper:%s, mongo.reducer:%s, "
                           "tempCollectionName:%s, queryKey:%s, queryResult:%s, result:%s"
                           % (str(mongo.mapper), str(mongo.reducer), mongo_settings.tempCollectionName, queryKey, queryResult, result))

        # Create a cursor, this is different than in pymongo where result.find will give you a document
        motorCursor = result.find()

        # For each of the mapReduceResult, which is now a dictionary of user, and list of videoId (string)
        while (yield motorCursor.fetch_next):
            # Get the next object from motorCursur
            mapReduceResult = motorCursor.next_object()

            # We will get each of the videoId when we split the string of videoId's, and we cast a
            # set in order to make the list unique, since a user can comment on the same videos
            for videoId in set(mapReduceResult["value"].split(',')):
                # For each of the find all the comments that a user commented inside a unique videoId
                # which means all the comments in a video. This is able to find multiple comments
                # a user commented inside a video

                # Get the cursor to find the comments according to videoId and userName
                commentsMotorCursur = mongo.client.youtube.comments.find({"videoId":videoId, "username":mapReduceResult["_id"]})

                # Fetch the next comments
                while (yield commentsMotorCursur.fetch_next):
                    # Get the next comment
                    comment = commentsMotorCursur.next_object()

                    # Add the next comment into user_video collection
                    result = yield mongo.insert_aggregate_user_video(mongo.client, mapReduceResult, comment)
                    logger.logger.info("insert_aggregate_user_video, mapReduceResult:%s, comment:%s, result:%s"
                                       % (mapReduceResult, comment, result))

        # Returns a JSON query response to the user indicating that the
        # search is done
        response = {'success': 'true',
                    "results": [{"title": "Search Done!"}]}

        # Send the json response back to the web browser
        self.write(response)
