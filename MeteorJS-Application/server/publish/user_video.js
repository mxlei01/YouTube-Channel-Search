// This is used to get data from the user_video collections
// We will get a channelID, where we will filter the data based on the channelID
Meteor.publish("user_video", function (channelId)
{
    // Create a search document, and only find the channelID's that exist under every user
    searchDocument = {};
    searchDocument[channelId] = { '$exists' : 1 };
    return user_videos.find(searchDocument);
});