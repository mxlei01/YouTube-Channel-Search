// Create Mongo Collection: comments
// comments:
//      _id = id (of comments)
//      channelName
//      Username
//      textDisplay
//      Date_Of_Comment
//      channelID
//      videold
//      Title
//      Description
//      Date_Of_Video
comments = new Mongo.Collection("comments");

//Create Mongo Collection: user_video
// _id:Username
//	{Video1, channelID}
//		Comments
//		Comments
//	{Video1, channelID}
//		Comments
//		Comments
//	{Video1, channelID}
//		Comments
user_videos = new Mongo.Collection("user_video");

// Code ran at the server
if (Meteor.isServer)
{
    Meteor.publish("comments", function (search, type)
    {
        // If type == 1, then we will search using channelID, and
        // if type == 0, then we will search using channelName
        if (type == "1")
        {
            return comments.find({channelId : search});
        }
        else if (type == "0")
        {
            // Need to make sure that the channelName is not empty, because it is possible that
            // a collection have some rows that does not have a channel name, and only channel ID
            // and the user selected to search by channel name, but have not typed in any channel name
            // it will actually accidentally search for channel name that are empty, and will return
            // a lot of data
            if (search != "")
            {
                return comments.find({channelName: search});
            }
        }
    });
    Meteor.publish("user_video", function (channelId)
    {
        // Create a search document, and only find the channelID's that exist under every user
        searchDocument = {};
        searchDocument[channelId] = { '$exists' : 1 };
        return user_videos.find(searchDocument);
    });
}

// Code ran at the client
if (Meteor.isClient)
{
    // Store subscriptions so that we can stop them later
    var commentSubscribe = null;
    var userVideoSubscribe = null;

    // Keep track of the channelId that we retrieve from comments
    var channelId = "";

    Template.body.helpers
    (
        {
            commentsCount: function()
            {
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
                array = [];
                user_videos.find().forEach(function(users)
                {
                    array.push({'_id':users['_id'], 'videos':users[channelId], 'time':users["dateOfReply"]});
                });
                return array
            }
        }
    );

    // jQuery waits until the documents is fully loaded
    $( document ).ready(function()
    {
        // Initializes the search UI
        $('.ui.search')
            .search
            (
                {
                    apiSettings:
                    {
                        beforeSend: function (settings)
                        {
                            // Subscribe to comments collection, and will filter based on the value
                            // the user typed in the search box, and also stop the last subscription
                            try
                            {
                                commentSubscribe.stop();
                            } catch(err) {}
                            commentSubscribe = Meteor.subscribe("comments", $('.ui.search').search('get value'), $('.ui.dropdown').dropdown('get value'));

                            // Changes a header showing the user what was searched
                            $('#userSearch').text($('.ui.search').search('get value'));

                            // Add a loading icon to the search bar before we sent our request
                            // to the tornado server
                            $('.ui.search').addClass("loading");

                            // If the dropdown value is 0, it means that we are searching
                            // by username, if the dropdown value is 1, then it means we are searching
                            // by channel ID
                            if ($('.ui.dropdown').dropdown('get value') == "1")
                            {
                                // If searching by channel ID, then we will populate the ID portion
                                // of the request
                                settings.url = settings.url + 'name=&id='
                                    + $('.ui.search').search('get value');
                            }
                            else if ($('.ui.dropdown').dropdown('get value') == "0")
                            {
                                // If searching by user name, then we will populate the name portion
                                // of the request
                                settings.url = settings.url + 'id=&name='
                                    + $('.ui.search').search('get value');
                            }

                            // returns the setting.url that we have modified
                            return settings;
                        },
                        // Base URL settings, according to the dropdown, we will either populate a
                        // Channel ID or user name, but not both (limitation of youtube API v3)
                        url: 'http://192.168.219.130:8888/channel?'
                    }
                }
            )

        // Initialize a dropdown, so that users can select between Channel ID, and User Name
        // if dropdown is not initialized, it will not work
        $('.ui.dropdown').dropdown({});
    });
}