# YouTube-Channel-Search
Searches a channel in Youtube, and lists out all the user's comments, based on MeteorJS, Tornado, and MongoDB.

<h1> How to Setup: </h1>
1. Install Tornado, Motor, PyMongo, MeteorJS, and MongoDB.
2. Use default settings for MongoDB.
3. You can call python main.py in the Tornado application folder, and it will startup a tornado application connecting to the default settings for MongoDB (localhost, and 27017 port).
4. Use the included run.sh in the MeteorJS application folder to start the MeteorJS application directly on a local database.
5. There are two input support when you first visit localhost:3000.
    A. channel ID: when you see a youtube URL that has channel/38dk4j3k4jd83, the "38dk4j3k4jd83" is a channel ID, so please use the channel ID search mode
    B. user name : when you see a youtube URL that has user/someName, the "someName" is a username, so please use the username search mode.
