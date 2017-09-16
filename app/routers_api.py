from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree.ElementTree import fromstring

AUTH_URL = "https://commerce.reuters.com/rmd/rest/xml/"
SERVICE_URL = "http://rmb.reuters.com/rmd/rest/xml/"


class RoutersAPI:
    def __init__(self):
        self.authToken = '0Uar2fCpykWdpaNseln+nzU0j1MmIwWV81kIX5wuiTI='

    def get_token(self):
        tree = self._call('login', {'username': 'HackZurichAPI', 'password': '8XtQb447'}, True)
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

    def _call(self, method, args=None, auth=False):
        if args is None:
            args = {}

        if auth:
            root_url = AUTH_URL
        else:
            root_url = SERVICE_URL
            args['token'] = self.authToken
        url = root_url + method + '?' + urlencode(args)
        resp = urlopen(url, timeout=10)
        rawd = resp.read()
        return fromstring(rawd)  # parse xml

    def call(self, method, args={}):
        return self._call(method, args, False)

    def recent_news(self, channel):
        return self.call('items',
                         {'channel': channel,
                          'maxAge': '120m',
                          'mediaType': 'T'})
