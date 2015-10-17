import tornado.web
from tornado import gen
from concurrent import futures
import coroutines
import synchronous
import executors
import youtube_api
import settings
import logger
import mongo
import mongo_settings

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

        # We only choose between channelID, or channelName, and not both since
        # both cannot exists in the same time using the youtube's channel API, otherwise
        # it will throw an error
        channelAPI = None
        if channelID:
            channelAPI = youtube_api.getChannels_withID % (channelID, settings.youtube_API_key, "")
        else:
            channelAPI = youtube_api.getChannels % (channelName, settings.youtube_API_key, "")

        return channelAPI

    @gen.coroutine
    def getChannelData(self, channelName, channelID, loopFlags):
        # Usage:
        #       Since only channelName or channelID is populated, we will test
        #       if channelName or channelID exists. If channelName exists, then
        #       we will use youtube_api.getChannelAPI, else youtube_api.getChannels_withID
        # Arguments:
        #       channelName: name of a channel
        #       channelID  : ID of a channel
        #       loopFlags  : a dictionary of flags that indicate whether if there are next set
        #                    of json data whether channel/video/comment/commentThread
        #                    that we need
        # Return:
        #       None

        # Determine the API that we are going to use, whether it is primary channelName or channelID
        # since you cannot use both channelName or channelID to get channel information
        # Using the channelName/channelID, we would get the channel information
        # with youtube's channels API. This will not only give us the multiple channels embedded in a
        # channel, but it would also convert channelName into channelID, and videos associate themselves
        # with channelID, not channelName.
        getChannelAPI = self.getChannelAPI(channelName, channelID)

        # Loop through if nextPageToken exists, this means that either this is at the first run
        # or the the results of channels > 50
        while loopFlags["channelNextPageToken"]:
            # Using the getChannelAPI we created previously, we will feed this into a coroutine, and
            # the asyncHTTPClient will help us to get the results asynchronously
            channelNameJson = yield coroutines.fetch_coroutine(getChannelAPI)
            logger.logger.info("channelName:%s, channelID:%s, getChannelAPI:%s, channelNameJson:%s" % (channelName, channelID, getChannelAPI, channelNameJson))

            # Sometimes a fetch can fail, and return None
            if channelNameJson:
                # Loop through each channel ID inside the json array with the key items
                # this will essentially give us all the independent channel ID's in a channelName/ChannelID
                # (this means that the channel owner subscribed to multiple channels)
                for channelID in channelNameJson["items"]:
                    # Create a getVideos api string, this will essentialy let us to get all the videoID's
                    # associated within a channel, and videoID's are unique strings, and we will use
                    # the videoID's to get comments later
                    getVideosAPI = youtube_api.getVideos % (channelID["id"], settings.youtube_API_key, "")

                    # A flag to indicate that we have more pages to search for, we will need to set this
                    # for every channel, since if this is not re-initialized to True, it will not
                    # loop through the next channels if there are any
                    loopFlags["videosNextPageToken"] = True

                    # Loop through videos if nextPageToken exists, either at first loop or
                    # meaning results are > 50 for videos
                    while loopFlags["videosNextPageToken"]:
                        # Using the getVideosAPI that we created to get videoID's, we would feed this
                        # into a coroutine to grab the results asynchronously
                        videosJson = yield coroutines.fetch_coroutine(getVideosAPI)
                        logger.logger.info("getVideosAPI:%s, videosJson:%s" % (getVideosAPI, videosJson))

                        # Sometimes a fetch can fail, and return None
                        if videosJson:
                            # Loop through each video information using the "items" key, this will
                            # essentially give us all the unique video ID, and name for each video
                            for video in videosJson["items"]:
                                # We will need to check if videoId key exists in the video["id"] key, since this will
                                # tell us whether the item we are looking at a video entry,
                                # because sometimes if the channel/user subscribed to a channel
                                # it will also appear in as a "video" item
                                if "videoId" in video["id"]:
                                    # Create a getCommentThread api string, this essentially will give us all the
                                    # video's top level comments. These are all the comments directly commenting the video itself, and
                                    # there's another type which are reply comments, which are comments replied to a top level comment.
                                    # We can also get the comment username, comment text, and comment date.
                                    getCommentThreadAPI = youtube_api.getCommentThread % (video["id"]["videoId"], settings.youtube_API_key, "")

                                    # A flag to indicate that we have more comments to go through, we would need to re-intialized this
                                    # everytime we get comment threads for a video, because when we get to the next video, if we don't
                                    # set this back to True, then it will not find the next videos
                                    loopFlags["commentThreadNextPageToken"] = True

                                    # Loop through next set of comments if results > 100,
                                    # or if we are at the first iteration
                                    while loopFlags["commentThreadNextPageToken"]:
                                        # Fetch the comments for a specific video, we will feed this into a coroutine
                                        # to get us json data for comments in a specific videoID asynchronously
                                        commentThreadJson = yield coroutines.fetch_coroutine(getCommentThreadAPI)
                                        logger.logger.info("getCommentThreadAPI:%s, commentThreadJson:%s" % (getCommentThreadAPI, commentThreadJson))

                                        # Sometimes a fetch can fail, and return None
                                        if commentThreadJson:
                                            # Loop through each top level comments, this will essentially give us
                                            # all the comments for a videoID, and we can use this data to record the username, user comment,
                                            # and date
                                            for topComment in commentThreadJson["items"]:
                                                # We will insert the video information itself, such as videoID, title, description, and
                                                # when it's published, and also username, user comments, and date, and this is an
                                                # indepotent action, where if we did this multiple times, the result is the same
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

                                                # If the totalReplyCount > 0, then we know that there are replies
                                                # to this comment
                                                if topComment["snippet"]["totalReplyCount"] > 0:
                                                    # Create a getCommentReplies api string, this will also give us the same information
                                                    # as top level comment for users, such as their username, user comment, and date
                                                    # but aimed at replies instead of top level comments
                                                    getCommentRepliesAPI = youtube_api.getCommentReplies % (topComment["id"], settings.youtube_API_key, "")

                                                    # A flag to indicate that we have more replies to go through, again, we need to
                                                    # initialize this at the start to True for every top level comment replies we want to find
                                                    # otherwise it will not find the replies for top level comment for the next video
                                                    loopFlags["commentRepliesNextPageToken"] = True

                                                    # Loop through each set of replies if > 100 results, or this is the first run
                                                    while loopFlags["commentRepliesNextPageToken"]:
                                                        # Fetch the replies for a specific comment by feeding this URL into
                                                        # a coroutine, so that we can fetch the data asynchronously
                                                        commentRepliesJson = yield coroutines.fetch_coroutine(getCommentRepliesAPI)
                                                        logger.logger.info("getCommentRepliesAPI:%s, commentRepliesJson:%s" % (getCommentRepliesAPI, commentRepliesJson))

                                                        # Sometimes a fetch can fail, and return None
                                                        if commentRepliesJson:
                                                            # Loop through each top comment replies, this will essentially give us
                                                            # the replies for a top level comment which includes the username
                                                            # and user comment, and date
                                                            for replies in commentRepliesJson["items"]:
                                                                # Store the data into MongoDB using the same API for inserting the top level comments
                                                                # except we will replies the top level comment data with replies data
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


                                                            # If next page token does not exist, means that there are no more replies for comment
                                                            # then we can stop the loop
                                                            if "nextPageToken" not in commentRepliesJson:
                                                                # If the nextPageToken does not exist, then we can end the while loop
                                                                loopFlags["commentRepliesNextPageToken"] = False
                                                            else:
                                                                # If it does exist, then we build the getCommentRepliesAPI with the next page token to go the next set of top level replies
                                                                getCommentRepliesAPI = youtube_api.getCommentReplies % (topComment["id"], settings.youtube_API_key, commentRepliesJson["nextPageToken"])

                                        # If next page token does not exist, means that there are no more comments for the video
                                        # then we can stop the loop
                                        if "nextPageToken" not in commentThreadJson:
                                            # If the nextPageToken does not exist, then we can end the while loop
                                            loopFlags["commentThreadNextPageToken"] = False
                                        else:
                                            # If it does exist, then we build the getCommentThreadAPI with the next page token to go the next set of top level comments
                                            getCommentThreadAPI = youtube_api.getCommentThread % (video["id"]["videoId"], settings.youtube_API_key, commentThreadJson["nextPageToken"])

                            # If next page token does not exist, means that there are no more videos in a channel left
                            # then we can stop the loop
                            if "nextPageToken" not in videosJson:
                                # If the nextPageToken does not exist, then we can end the while loop
                                loopFlags["videosNextPageToken"] = False
                            else:
                                # If it does exist, then we build the getVideosAPI with the next page token to go the next set of videos
                                getVideosAPI = youtube_api.getVideos % (channelID["id"], settings.youtube_API_key, videosJson["nextPageToken"])

                # If next page token does not exist, means that there are no more channels left
                # then we can stop the loop
                if "nextPageToken" not in channelNameJson:
                    # If the nextPageToken does not exist, then we can end the while loop
                    loopFlags["channelNextPageToken"] = False
                else:
                    # If it does exist, then we build the getChannelAPI with the next page token, we can go to the next set of channels
                    getChannelAPI = self.getChannelAPI(channelName, channelID)

    def getQueryKeyAndResult(self, channelName, channelID):
        # Usage:
        #       This will return a key and value to aggregate videos under a user with
        #       a specific channelName or channelID
        # Arguments:
        #       channelName : channel's Name
        #       channelID   : channel's ID
        # Return:
        #       tuple of either ("channelID", channelID) or ("channelName", channelName)

        # Determine if channelID exists provided by the user
        if channelID:
            return ("channelID", channelID)
        else:
            return ("channelName", channelName)

    @gen.coroutine
    def aggregateUserVideos(self, queryKey, queryResult):
        # Usage:
        #       We need to query the data for videos and users, we can do this by mapping all
        #       videos with username, and videoID, and then aggregating all the same key (user names)
        #       to videoID. We can filter out the videos that do not fall under a specific Channel Name
        #       or channel ID by using query={queryKey:queryResult}.
        #       The result of the data would look like:
        #       _id:Username
        # 	        {Video1, channelName/channelID}
        #		        Comments
        #		        Comments
        #	        {Video2, channelName/channelID}
        #		        Comments
        #		        Comments
        #	        {Video3, channelName/channelID}
        #		        Comments
        # Arguments:
        #       queryKey    : key of query to query the comment table against to get
        #                     only all videos under a specific channel name or channel ID.
        #                     the variable must only contain the string "channelName" or "channelID"
        #       queryResult : value of the channel name or channel ID
        # Return:
        #       None

        # We will get all the users (people who made comments) and their videos of what they commented on.
        # Data will look like:
        #   user_name_1 :
        #           video1
        #           video2
        #   user_name_2 :
        #           video1
        #           video3
        # Later using this data, we can get all the comments they made under a specific video
        result = yield mongo.aggregate_user_videoId(mongo.client, mongo.mapper, mongo.reducer, mongo_settings.tempCollectionName, queryKey, queryResult)
        logger.logger.info("aggregate_user_videoId, mongo.mapper:%s, mongo.reducer:%s, "
                           "tempCollectionName:%s, queryKey:%s, queryResult:%s, result:%s"
                           % (str(mongo.mapper), str(mongo.reducer), mongo_settings.tempCollectionName, queryKey, queryResult, result))

        # Create a cursor, this is different than in pymongo where result.find will give you a document
        motorCursor = result.find()

        # For each of the mapReduceResult, which is now a dictionary of user, and list of videoId (string)
        while (yield motorCursor.fetch_next):
            # Get the next object from motorCursor, which is from fetch_next, this will now
            # be a dictionary form of {"_id":"username", "value":"video1, video2, video3"}
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
    @gen.coroutine
    def get(self):
        # Usage:
        #       We will use youtube's api to get the channel information
        #       which include channel information, videos, and user comments, and add the
        #       data into mongodb, and then does a map reduce to aggregate data into
        #       specific users with all the videos they commented on.
        # Arguments:
        #       None
        # Return:
        #       None

        # Get channel name and channel ID (one of them are empty)
        channelName = self.get_argument('name')
        channelID = self.get_argument('id')

        # Setup neccessary flags we need to determine if there is a "next" page in the
        # json response, since a json response can only be 50~100 independent items long,
        # if a user have more than 50 videos, and in each comment, there are more than 50 comments
        # then we need to loop through all the lists.
        # channelNextPageToken        = if more than 50 channels are present
        # videosNextPageToken         = if more than 50 videos are present per channel (above)
        # commentThreadNextPageToken  = if more than 100 comment threads per video (above)
        # commentRepliesNextPageToken = if more than 100 replies per comment thread (above)
        # they are all setup as true, so that we can determine if there are more data by checking
        # for "nextPageToken" later
        loopFlags = dict.fromkeys(["channelNextPageToken", "videosNextPageToken",
                                   "commentThreadNextPageToken", "commentRepliesNextPageToken"], True)

        # Use the channelName, channelID, and loopFlags, find all the user comments, and insert them
        # into MongoDB
        yield self.getChannelData(channelName, channelID, loopFlags)

        # Get the queryKey and queryResult depending on if the user has provided a
        # channelID. This will be used to aggregate based on channel name or channel ID, because
        # the user can search either by channel name or channel ID, and we want to aggregate one
        # of them.
        queryKey, queryResult = self.getQueryKeyAndResult(channelName, channelID)

        # The next part of the task is to aggregate the data, where we want to get all the videos
        # in a specific channel that matches to a username.
        yield self.aggregateUserVideos(queryKey, queryResult)

        # Returns a JSON query response to the user indicating that the
        # search is done
        self.write({'success': 'true',
                    "results": [{"title": "Search Done!"}]})
