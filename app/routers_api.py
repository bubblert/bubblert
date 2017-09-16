from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree.ElementTree import fromstring

import re

AUTH_URL = "https://commerce.reuters.com/rmd/rest/xml/"
SERVICE_URL = "http://rmb.reuters.com/rmd/rest/xml/"

NAMESPACE = "http://iptc.org/std/nar/2006-10-01/"

class RoutersAPI:
    def __init__(self):
        self.authToken = '0Uar2fCpykWdpaNseln+nzU0j1MmIwWV81kIX5wuiTI='

    def get_token(self):
        tree = self._call_xml('login', {'username': 'HackZurichAPI', 'password': '8XtQb447'}, True)
        if tree.tag == 'authToken':
            self.authToken = tree.text
        else:
            raise Exception('unable to obtain authToken')

    def get_channels(self):
        return [
            'BEQ259',
            'FES376',
            'STK567',
            'Wbz248'
        ]

    def _call_raw(self, method, args=None, auth=False):
        if args is None:
            args = {}

        if auth:
            root_url = AUTH_URL
        else:
            root_url = SERVICE_URL
            args['token'] = self.authToken
        url = root_url + method + '?' + urlencode(args)
        resp = urlopen(url, timeout=10)
        return resp.read().decode("UTF-8")

    def _call_xml(self, method, args=None, auth=False):
        return fromstring(self._call_raw(method, args, auth))

    def call(self, method, args={}):
        return self._call_xml(method, args, False)

    def recent_news(self, channel):
        return self.call('items',
                         {'channel': channel,
                          'maxAge': '120m',
                          'mediaType': 'T'})

    def get_story(self, item_id):
        try:
            item_str = self._call_raw('item', {'id': item_id})
        except HTTPError:
            return None

        body = self.find_between(item_str, "<body>", "</body>")
        xml = fromstring(item_str)

        for c in xml.findall('.//{%s}remoteContent' % NAMESPACE):
            item_id = c.findtext('id')

        return {
            'body': body,
            'dateline': xml.findtext('.//{%s}dateline' % NAMESPACE),
        }

    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""
