Template.body.helpers
(
    {
        commentsCount: function()
        {
            // get the channel ID that we are querying against, so that we can display
            // this channel ID on front of the webpage
            try
            {
                channelId = comments.findOne().channelId;
            }
            catch(err){}

            // subscribe to the user_comments where the channelID is what we recieved from any comments
            // any comments would have the same channelId, and also remove the last subscription
            try
            {
                userVideoSubscribe.stop();
            } catch(err) {}
            userVideoSubscribe = Meteor.subscribe("user_video", channelId);

            // Returns the total count of comments for the channel
            return comments.find().count()
        },
        uniqueUserCount: function()
        {
            // Returns a unique number of usernames
            return _.uniq(comments.find({}, {
                sort: {username: 1}, fields: {username: true}
            }).fetch().map(function(x) {
                return x.username;
            }), true).length;
        },
        uniqueVideosCount: function()
        {
            // Returns a unique number of videoId's
            return _.uniq(comments.find({}, {
                sort: {videoId: 1}, fields: {videoId: true}
            }).fetch().map(function(x) {
                return x.videoId;
            }), true).length;
        },
        user_videos: function()
        {
            // Returns each user's comment's for each video, users[channelId] is an array
            // of user comments.
            array = [];
            user_videos.find().forEach(function(users)
            {
                array.push({'_id':users['_id'], 'videos':users[channelId], 'time':users["dateOfReply"]});
            });
            return array
        }
    }
);