"""
 Google (News)

 @website     https://news.google.com
 @provide-api no

 @using-api   no
 @results     HTML
 @stable      no
 @parse       url, title, content, publishedDate
"""

from lxml import html
from searx.engines.google import _fetch_supported_languages, supported_languages_url
from searx.url_utils import urlencode
from searx.utils import match_language

# search-url
categories = ['news']
paging = True
language_support = True
safesearch = True

number_of_results = 10

search_url = 'https://www.google.com/search'\
    '?{query}'\
    '&tbm=nws'\
    '&gws_rd=cr'\
    '&{search_options}'


# do search-request
def request(query, params):

    search_options = {
        'start': (params['pageno'] - 1) * number_of_results
    }

    if safesearch and params['safesearch']:
        search_options['safe'] = 'on'

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      search_options=urlencode(search_options))

    if params['language'] != 'all':
        language = match_language(params['language'], supported_languages, language_aliases).split('-')[0]
        if language:
            params['url'] += '&lr=lang_' + language

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath('//div[@class="g"]|//div[@class="g _cy"]'):
        try:
            r = {
                'url': result.xpath('.//a[@class="l lLrAF"]')[0].attrib.get("href"),
                'title': ''.join(result.xpath('.//a[@class="l lLrAF"]//text()')),
                'content': ''.join(result.xpath('.//div[@class="st"]//text()')),
            }
        except:
            continue

        imgs = result.xpath('.//img/@src')
        if len(imgs) and not imgs[0].startswith('data'):
            r['img_src'] = imgs[0]

        results.append(r)

    # return results
    return results
