[![Build Status](https://travis-ci.org/mxlei01/YouTube-Channel-Search.svg?branch=master)](https://travis-ci.org/mxlei01/YouTube-Channel-Search)

# YouTube-Channel-Search
<p>Searches a channel in Youtube, and lists out all the user's comments, based on MeteorJS, Tornado, and MongoDB.</p>

<h1> How to Setup: </h1>
1. Install Tornado, Motor, PyMongo, MeteorJS, and MongoDB.
2. Use default settings for MongoDB.
3. You can call python main.py in the Tornado application folder, and it will startup a tornado application connecting to the default settings for MongoDB (localhost, and 27017 port).
4. Use the included run.sh in the MeteorJS application folder to start the MeteorJS application directly on a local database.
5. There are two input support when you first visit localhost:3000.
    <p>A. channel ID: when you see a youtube URL that has channel/38dk4j3k4jd83, the "38dk4j3k4jd83" is a channel ID then use the channel ID search mode</p>
    <p>B. user name : when you see a youtube URL that has user/someName, the "someName" is a username then use the user name search mode</p>
6. Setup an API key in the settings.py file, you will need to go to the developer console in google, and select youtube data API.

A Dockerfile that you can use to build the application, but you still need to complete step 6. You can look at the automated build at: https://hub.docker.com/r/mxlei01/youtube-channel-search/ to see how it's setup.

A .travis.yaml file is included, and a push to the repository will run a few tests, for example, testing if the youtube API in the tornado application works return expected values. Build is located at: https://travis-ci.org/mxlei01/YouTube-Channel-Search. It also pushes the image to https://hub.docker.com/r/mxlei01/youtube-channel-search-travis/.

<h1> Implementation Details: </h1>

<p> <b>MeteorJS</b> </p>
<p> The main page in MeteorJS has a dropdown to search for youtube comment using a Channel Name or Channel ID. Either option sends a request to Tornado through a GET request. The Tornado application inserts data into MongoDB, and the MeteorJS application is updated with the results. </p>

<p> <b>Tornado</b> </p>
<p> When it recieves a get request from the MeteorJS application, it will search for all user comments for a given channel. It does this by looping into 4 conditions:</p>
1. Searches for all the channels inside a given channel.
2. For each channel from step 1, search for all the video's, which essentially gets all the video names and video ID (unique)
3. For each video ID from step 2, search for all the top level replies, which are replies on the video itself, note that people can also reply on a reply. At this step, we will insert a row of user ID, comments, video ID, video name into the database.
4. For each top level reply from step 3, look at totalReplies key from the JSON file, and if it is greater than 0, then we will use another API to get all the replies for a top level reply. Furthermore, we will insert a row of user ID, comments, video ID, and video name into the database like step 3.

<p> The next step is to perform a map reduce operation to aggregate all user's comments by respective videos, and store them in the database, and this is the data that the MeteorJS application uses </p>
