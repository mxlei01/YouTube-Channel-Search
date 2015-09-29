// Create Mongo Collection: comments
// comments:
//      _id = id (of comments)
//      Username
//      textDisplay
//      Date_Of_Comment
//      channelID
//      videold
//      Title
//      Description
//      Date_Of_Video
comments = new Mongo.Collection("comments");

// Code ran at the server
if (Meteor.isServer)
{
    Meteor.publish("comments", function ()
    {
        //return comments.find();
    });
}

// Code ran at the client
if (Meteor.isClient)
{
    Template.body.helpers
    (
        {
            comments: function ()
            {
                return comments.find()
            }
        }
    );

    Meteor.subscribe("comments");
}