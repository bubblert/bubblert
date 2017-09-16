from os import environ
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree.ElementTree import fromstring

import re


class RoutersAPI:
    def __init__(self):
        self.authToken = environ.get('REUTERS_TOKEN')

    def get_token(self):
        tree = self._call_xml('login', {
            'username': environ.get('REUTERS_USERNAME'),
            'password': environ.get('REUTERS_PASSWORD')
        }, True)
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
            root_url = environ.get('AUTH_URL')
        else:
            root_url = environ.get('SERVICE_URL')
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

    def get_story_highlight(self, item_id):

        try:
            item_str = self._call_raw('item', {'id': item_id})
        except HTTPError:
            return None

        stripped_str = re.sub('<inlineXML.*</inlineXML>', '', item_str, flags=re.DOTALL)
        stripped_str = re.sub('<newsMessage.*?>', '<newsMessage>', stripped_str, flags=re.DOTALL, count=1)
        stripped_str = re.sub('rtr:', '', stripped_str, flags=re.DOTALL)

        xml = fromstring(stripped_str)

        image = None
        for c in xml.findall('.//remoteContent[@contenttype=\'image/jpeg\']'):
            image = c.attrib['href']
            break

        return {'image': '{}?token={}'.format(image, self.authToken) if image is not None else None,
                'keywords': [c.text for c in xml.findall('.//keyword')]}

    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""
