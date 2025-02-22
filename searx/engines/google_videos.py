"""
 Google (Videos)

 @website     https://www.google.com
 @provide-api yes (https://developers.google.com/custom-search/)

 @using-api   no
 @results     HTML
 @stable      no
 @parse       url, title, content, thumbnail
"""

from datetime import date, timedelta
from json import loads
from lxml import html
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode
import re

# engine dependent config
categories = ['videos']
paging = True
safesearch = True

number_of_results = 10

search_url = 'https://www.google.com/search'\
    '?q={query}'\
    '&tbm=vid'\
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
    for result in dom.xpath('//div[@class="g"]'):

        title = extract_text(result.xpath('.//h3'))
        url = result.xpath('.//div[@class="r"]/a/@href')[0]
        content = extract_text(result.xpath('.//span[@class="st"]'))

        # get thumbnails
        script = str(dom.xpath('//script[contains(., "_setImagesSrc")]')[0].text)
        ids = result.xpath('.//div[@class="s"]//img/@id')
        if len(ids) > 0:
            thumbnails_data = \
                re.findall('s=\'(.*?)(?:\\\\[a-z,1-9,\\\\]+\'|\')\;var ii=\[(?:|[\'vidthumb\d+\',]+)\'' + ids[0],
                           script)
            tmp = []
            if len(thumbnails_data) != 0:
                tmp = re.findall('(data:image/jpeg;base64,[a-z,A-Z,0-9,/,\+]+)', thumbnails_data[0])
            thumbnail = ''
            if len(tmp) != 0:
                thumbnail = tmp[-1]

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'thumbnail': thumbnail,
                        'template': 'videos.html'})

    return results
