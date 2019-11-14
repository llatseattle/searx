"""
 Google (Images)

 @website     https://www.google.com
 @provide-api yes (https://developers.google.com/custom-search/)

 @using-api   no
 @results     HTML chunks with JSON inside
 @stable      no
 @parse       url, title, img_src
"""

from datetime import date, timedelta
from json import loads
from lxml import html
from searx.url_utils import urlencode

# engine dependent config
categories = ['images']
paging = True
safesearch = True

number_of_results = 100

search_url = 'https://www.google.com/search'\
    '?{query}'\
    '&tbm=isch'\
    '&yv=2'\
    '&{search_options}'


# do search-request
def request(query, params):
    search_options = {
        'ijn': params['pageno'] - 1,
        'start': (params['pageno'] - 1) * number_of_results
    }
    if safesearch and params['safesearch']:
        search_options['safe'] = 'on'

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      search_options=urlencode(search_options))

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath('//div[contains(@class, "rg_meta")]/text()'):

        try:
            metadata = loads(result)
            img_format = "{0} {1}x{2}".format(metadata['ity'], str(metadata['ow']), str(metadata['oh']))
            source = "{0} ({1})".format(metadata['st'], metadata['isu'])
            results.append({'url': metadata['ru'],
                            'title': metadata['pt'],
                            'content': metadata['s'],
                            'source': source,
                            'img_format': img_format,
                            'thumbnail_src': metadata['tu'],
                            'img_src': metadata['ou'],
                            'template': 'images.html'})

        except:
            continue

    return results
