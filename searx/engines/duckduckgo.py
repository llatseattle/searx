"""
 DuckDuckGo (Web)

 @website     https://duckduckgo.com/
 @provide-api yes (https://duckduckgo.com/api),
              but not all results from search-site

 @using-api   no
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content

 @todo        rewrite to api
"""

from lxml.html import fromstring
from json import loads
from searx.engines.xpath import extract_text
from searx.poolrequests import get
from searx.url_utils import urlencode
from searx.utils import match_language

# engine dependent config
categories = ['general']
paging = True
language_support = True
supported_languages_url = 'https://duckduckgo.com/util/u172.js'


language_aliases = {
    'ar-SA': 'ar-XA',
    'es-419': 'es-XL',
    'ja': 'jp-JP',
    'ko': 'kr-KR',
    'sl-SI': 'sl-SL',
    'zh-TW': 'tzh-TW',
    'zh-HK': 'tzh-HK'
}

# search-url
url = 'https://duckduckgo.com/html?{query}&s={offset}&dc={dc_param}'

# specific xpath variables
result_xpath = '//div[@class="result results_links results_links_deep web-result "]'  # noqa
url_xpath = './/a[@class="result__a"]/@href'
title_xpath = './/a[@class="result__a"]'
content_xpath = './/a[@class="result__snippet"]'


# match query's language to a region code that duckduckgo will accept
def get_region_code(lang, lang_list=[]):
    if lang == 'all':
        return None

    lang_code = match_language(lang, lang_list, language_aliases, 'wt-WT')
    lang_parts = lang_code.split('-')

    # country code goes first
    return lang_parts[1].lower() + '-' + lang_parts[0].lower()


def request(query, params):
    offset = (params['pageno'] - 1) * 30

    region_code = get_region_code(params['language'], supported_languages)
    params['url'] = 'https://duckduckgo.com/html/'
    if params['pageno'] > 1:
        params['method'] = 'POST'
        params['data']['q'] = query
        params['data']['s'] = offset
        params['data']['dc'] = 30
        params['data']['nextParams'] = ''
        params['data']['v'] = 'l'
        params['data']['o'] = 'json'
        params['data']['api'] = '/d.js'
        if region_code:
            params['data']['kl'] = region_code
    else:
        if region_code:
            params['url'] = url.format(
                query=urlencode({'q': query, 'kl': region_code}), offset=offset, dc_param=offset)
        else:
            params['url'] = url.format(
                query=urlencode({'q': query}), offset=offset, dc_param=offset)
    return params


# get response from search-request
def response(resp):
    results = []

    doc = fromstring(resp.text)

    # parse results
    for i, r in enumerate(doc.xpath(result_xpath)):
        if i >= 30:
            break
        try:
            res_url = r.xpath(url_xpath)[-1]
        except:
            continue

        if not res_url:
            continue

        title = extract_text(r.xpath(title_xpath))
        content = extract_text(r.xpath(content_xpath))

        # append result
        results.append({'title': title,
                        'content': content,
                        'url': res_url})

    # return results
    return results


# get supported languages from their site
def _fetch_supported_languages(resp):

    # response is a js file with regions as an embedded object
    response_page = resp.text
    response_page = response_page[response_page.find('regions:{') + 8:]
    response_page = response_page[:response_page.find('}') + 1]

    regions_json = loads(response_page)
    supported_languages = map((lambda x: x[3:] + '-' + x[:2].upper()), regions_json.keys())

    return list(supported_languages)
