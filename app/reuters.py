import urllib
from urllib.request import urlopen
import time
import logging
from xml.etree.ElementTree import ElementTree, fromstring
from settings import REUTERS_PASSWORD, REUTERS_USERNAME

AUTH_URL = "https://commerce.reuters.com/rmd/rest/xml/"
SERVICE_URL = "http://rmb.reuters.com/rmd/rest/xml/"


class Reuters:
    def __init__(self, username=REUTERS_USERNAME, password=REUTERS_PASSWORD):
        self.authToken = None

        tree = self._call('login', {'username': username, 'password': password}, True)
        if tree.tag == 'authToken':
            self.authToken = tree.text
        else:
            raise Exception('unable to obtain authToken')

    def _call(self, method, args={}, auth=False):
        if auth:
            root_url = AUTH_URL
        else:
            root_url = SERVICE_URL
            args['token'] = self.authToken

        url = root_url + method + '?' + urllib.parse.urlencode(args)
        logging.debug('> ' + url)
        resp = urlopen(url, timeout=10)
        rawd = resp.read()
        return fromstring(rawd)  # parse xml

    def call(self, method, args={}):
        return self._call(method, args, False)

    def get_story(self, story_id):
        args = {}
        args['id'] = story_id
        try:
            item = self.call('item', args)
        except urllib.error.HTTPError:
            return None

        for content in item.findall('contentSet'):
            print(content)

        return None

        # channels = [{'alias': c.findtext('alias'),
        #              'description': c.findtext('description')}
        #             for c in tree.findall('channelInformation')]
        # print
        # "List of channels:\n\talias\tdescription"
        # print
        # "\n".join(["\t%(alias)s\t%(description)s" % x for x in channels])
        #
        # # fetch id's and headlines for a channel
        # rd = Reuters()
        # tree = rd.call('items',
        #                {'channel': 'AdG977',
        #                 'channelCategory': 'OLR',
        #                 'limit': '10'})
        # items = [{'id': c.findtext('id'),
        #           'headline': c.findtext('headline')}
        #          for c in tree.findall('result')]
        # print
        # "\n\nList of items:\n\tid\theadline"
        # print
        # "\n".join(["\t%(id)s\t%(headline)s" % x for x in items])
