// Mongo Collection: user_video
//      This is a data structure to show the user what videos a user has commented on.
//      For example, under the _id:username, this we can list out the username, and then list out
//      all the video name, and under each video name, we can list out each independent comment the
//      user had commented on.
// Structure:
//  _id:Username
//      {Video1, channelID}
//		    Comments
//		    Comments
//	    {Video1, channelID}
//		    Comments
//		    Comments
//	    {Video1, channelID}
//		    Comments
user_videos = new Mongo.Collection("user_video");
