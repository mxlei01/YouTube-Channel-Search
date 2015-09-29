// Create Two Mongo Collection: video and user
// video:
//      _id = {channelID, videoId}
//      Title = title
//      Description = Description
//      Date = publishedAt
// user:
//      _id = {videold, id}
//      Username = username
//      textDisplay = textDisplay
//      Date = updatedAt
video = new Mongo.Collection("video");
user = new Mongo.Collection("user");

// Code ran at the server
if (Meteor.isServer)
{

}

// Code ran at the client
if (Meteor.isClient)
{

}