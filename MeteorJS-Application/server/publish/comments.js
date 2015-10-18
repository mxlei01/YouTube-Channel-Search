// Comments publisher, this is used to get data from the comments collection.
// Mainly used for statistical analysis, for example, finding unique user counts, video counts, etc.
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