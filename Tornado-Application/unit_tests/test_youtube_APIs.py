import json
import tornado
import router.router_settings as router_settings
from tornado.testing import AsyncTestCase
from helper_coroutines import http_client
from youtube import youtube_api


class Test_APIs(AsyncTestCase):
    @tornado.testing.gen_test
    def test_getChannels_withID(self):
        # Tests the getChannels_withID API with channel ID
        # The json response should contain a keyword youtube#channel
        channelID = "UC27HFwJdWZFhwllMtwdES-A"
        channelAPI = youtube_api.getChannels_withID % (channelID, router_settings.youtube_API_key, "")
        response = yield http_client.fetch_coroutine(channelAPI)
        self.assertIn("youtube#channel", json.dumps(response))

    @tornado.testing.gen_test
    def test_getChannels(self):
        # Tests the getChannels API with channel name
        # The json response should contain a keyword youtube#channel
        channelName = "Animenzzz"
        channelAPI = youtube_api.getChannels % (channelName, router_settings.youtube_API_key, "")
        response = yield http_client.fetch_coroutine(channelAPI)
        self.assertIn("youtube#channel", json.dumps(response))

    @tornado.testing.gen_test
    def test_getVideos(self):
        # Tests the getVideos API with channel ID
        # The json response should contain a keyword youtube#video
        channelID = "UC27HFwJdWZFhwllMtwdES-A"
        channelAPI = youtube_api.getVideos % (channelID, router_settings.youtube_API_key, "")
        response = yield http_client.fetch_coroutine(channelAPI)
        self.assertIn("youtube#video", json.dumps(response))

    @tornado.testing.gen_test
    def test_getCommentThread(self):
        # Tests the getCommentThread API with videoID
        # The json response should contain a keyword youtube#commentThreadListResponse
        videoID = "sEQf5lcnj_o"
        channelAPI = youtube_api.getCommentThread % (videoID, router_settings.youtube_API_key, "")
        response = yield http_client.fetch_coroutine(channelAPI)
        self.assertIn("youtube#commentThreadListResponse", json.dumps(response))

    @tornado.testing.gen_test
    def test_getCommentReplies(self):
        # Tests the getCommentThread API with commentID
        # The json response should contain a keyword youtube#comment
        commentID = "z134f5zqbovpdhky304cgfcwhr2xylrobtc0k"
        channelAPI = youtube_api.getCommentReplies % (commentID, router_settings.youtube_API_key, "")
        response = yield http_client.fetch_coroutine(channelAPI)
        self.assertIn("youtube#comment", json.dumps(response))