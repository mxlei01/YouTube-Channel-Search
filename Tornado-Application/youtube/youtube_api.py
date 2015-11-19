# youtube_api.py stores all the actions for the REST API for youtube

# getChannel is used to get data (such as channel ID, which is not equal to the name) for a specific channel using username
# Parameters:
#   forUsername : username of the channel
#   key         : API key
#   pageToken   : token of the page, can be blank or used with nextPageToken to get to the next page
#                 if the # of results is over maxResults value
getChannels = "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername=%s&maxResults=50&key=%s&pageToken=%s"

# getChannel_withID is used to get data (such as channel ID, which is not equal to the name) for a specific channel using ID
# Parameters:
#   forUsername : username of the channel
#   key         : API key
#   pageToken   : token of the page, can be blank or used with nextPageToken to get to the next page
#                 if the # of results is over maxResults value
getChannels_withID = "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id=%s&maxResults=50&key=%s&pageToken=%s"

# get each video information according to the channelID we get get from using getChannels
# Parameters:
#   channelID   : ID of a channel, this is not the username, for example
#                 coca cola's channel will's will be like Eirk3jd834jDD3
#   key         : API key
#   pageToken   : token of the page, can be blank or used with nextPageToken to get to the next page
#                 if the # of results is over maxResults value
getVideos = "https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=%s&maxResults=50&key=%s&pageToken=%s"

# get each comment thread according to the videold parameter given from the getVideos API
# a note is that this only gives each thread, and there might be replies per thread basis, and we need to
# use getCommentReplies to also get the replies for each thread if replies > 0
#   videoId     : this is the video's ID, and we can find that using the getVideos api
#   key         : API key
#   pageToken   : token of the page, can be blank or used with nextPageToken to get to the next page
#                 if the # of results is over maxResults value
getCommentThread = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&maxResults=100&videoId=%s&key=%s&pageToken=%s"

# get each replies for a comment thread according to it's
#   parentId    : this is the top level comment ID that we can get from getCommentThread api
#                 we can use this api to get all the replies for a top level comment
#   key         : API key
#   pageToken   : token of the page, can be blank or used with nextPageToken to get to the next page
#                 if the # of results is over maxResults value
getCommentReplies = "https://www.googleapis.com/youtube/v3/comments?part=snippet&maxResults=100&parentId=%s&key=%s&pageToken=%s"