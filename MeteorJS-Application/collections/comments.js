// Mongo Collection: comments
//      This data is for statistical usage, for example, if we search by the the Username
//      we can compute how many unique users have comments in all the videos for a given
//      channel Name or channel ID.
// Structure:
//  comments:
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
