# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import load_engine, duckduckgo
from searx.testing import SearxTestCase


class TestDuckduckgoEngine(SearxTestCase):

    def test_request(self):
        duckduckgo = load_engine({'engine': 'duckduckgo', 'name': 'duckduckgo'})

        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        

        dicto['language'] = 'de-CH'
        params = duckduckgo.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('duckduckgo.com', params['url'])
        self.assertIn('ch-de', params['url'])
        self.assertIn('s=0', params['url'])

        # when ddg uses non standard codes
        dicto['language'] = 'zh-HK'
        params = duckduckgo.request(query, dicto)
        self.assertIn('hk-tzh', params['url'])

        dicto['language'] = 'en-GB'
        params = duckduckgo.request(query, dicto)
        self.assertIn('uk-en', params['url'])

        # no country given
        dicto['language'] = 'en'
        params = duckduckgo.request(query, dicto)
        self.assertIn('us-en', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, duckduckgo.response, None)
        self.assertRaises(AttributeError, duckduckgo.response, [])
        self.assertRaises(AttributeError, duckduckgo.response, '')
        self.assertRaises(AttributeError, duckduckgo.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(duckduckgo.response(response), [])

        html = u"""
        <div class="result results_links results_links_deep web-result result--no-result">
            <div class="links_main links_deep result__body">
                <h2 class="result__title">
                </h2>
                <div class="no-results">No results</div>
                <div class="result__extras">
                </div>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = duckduckgo.response(response)
        self.assertEqual(duckduckgo.response(response), [])

        html = u"""
        <div class="result results_links results_links_deep web-result ">
            <div class="links_main links_deep result__body">
                <h2 class="result__title">
                    <a rel="nofollow" class="result__a" href="http://this.should.be.the.link/ű">
                        This <b>is</b> <b>the</b> title
                    </a>
                </h2>
                <a class="result__snippet" href="http://this.should.be.the.link/ű">
                    <b>This</b> should be the content.
                </a>
                <div class="result__extras">
                </div>
            </div>
        </div>
        """
        response = mock.Mock(text=html)
        results = duckduckgo.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'This is the title')
        self.assertEqual(results[0]['url'], u'http://this.should.be.the.link/ű')
        self.assertEqual(results[0]['content'], 'This should be the content.')

    def test_fetch_supported_languages(self):
        js = """some code...regions:{
        "wt-wt":"All Results","ar-es":"Argentina","au-en":"Australia","at-de":"Austria","be-fr":"Belgium (fr)"
        }some more code..."""
        response = mock.Mock(text=js)
        languages = list(duckduckgo._fetch_supported_languages(response))
        self.assertEqual(len(languages), 5)
        self.assertIn('wt-WT', languages)
        self.assertIn('es-AR', languages)
        self.assertIn('en-AU', languages)
        self.assertIn('de-AT', languages)
        self.assertIn('fr-BE', languages)
