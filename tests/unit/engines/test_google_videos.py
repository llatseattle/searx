from collections import defaultdict
import mock
from searx.engines import google_videos
from searx.testing import SearxTestCase


class TestGoogleVideosEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['safesearch'] = 1
        
        params = google_videos.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])

        dicto['safesearch'] = 0
        params = google_videos.request(query, dicto)
        self.assertNotIn('safe', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, google_videos.response, None)
        self.assertRaises(AttributeError, google_videos.response, [])
        self.assertRaises(AttributeError, google_videos.response, '')
        self.assertRaises(AttributeError, google_videos.response, '[]')

        html = r"""
        <div>
            <div>
                <div class="g">
                    <div class="r">
                        <a href="url_1"><h3>Title 1</h3></a>
                    </div>
                    <div class="s">
                        <div>
                            <a>
                                <g-img>
                                    <img id="vidthumb1">
                                </g-img>
                            </a>
                        </div>
                    </div>
                    <div>
                        <span class="st">Content 1</span>
                    </div>
                </div>
                <div class="g">
                    <div class="r">
                        <a href="url_2"><h3>Title 2</h3></a>
                    </div>
                    <div class="s">
                        <div>
                            <a>
                                <g-img>
                                    <img id="vidthumb2">
                                </g-img>
                            </a>
                        </div>
                    </div>
                    <div>
                        <span class="st">Content 2</span>
                    </div>
                </div>
            </div>
        </div>
        <script>function _setImagesSrc(c,d,e){}</script>
        """
        response = mock.Mock(text=html)
        results = google_videos.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['url'], u'url_1')
        self.assertEqual(results[0]['title'], u'Title 1')
        self.assertEqual(results[0]['content'], u'Content 1')
        self.assertEqual(results[1]['url'], u'url_2')
        self.assertEqual(results[1]['title'], u'Title 2')
        self.assertEqual(results[1]['content'], u'Content 2')
