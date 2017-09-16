import urllib
from urllib.request import urlopen
import time
import logging
from xml.etree.ElementTree import ElementTree, fromstring, tostring
from settings import REUTERS_PASSWORD, REUTERS_USERNAME

from bs4 import BeautifulSoup
import re

AUTH_URL = "https://commerce.reuters.com/rmd/rest/xml/"
SERVICE_URL = "http://rmb.reuters.com/rmd/rest/xml/"
XML_NAMESPACE = 'http://iptc.org/std/nar/2006-10-01'


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

    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def get_story(self, story_id):
        args = {}
        args['id'] = story_id
        try:
            item = self.call('item', args)
        except urllib.error.HTTPError as e:
            logging.error(e)
            return None

        # this is hacky, namespace issues
        item_str = tostring(item).decode('utf-8')
        item_str = item_str.replace('<ns0:', '<').replace('<ns1:', '<').replace("<html:", "<")
        item_str = item_str.replace('</ns0:', '</').replace('</ns1:', '</').replace("</html:", "</")

        soup = BeautifulSoup(item_str, 'lxml')
        headline = soup.find('headline')
        if headline:
            headline = headline.text
        located = soup.find('located')
        if located:
            located = located.text
        created = soup.find('dateline')
        if created:
            created = created.text
        tldr = soup.find('description')
        if tldr:
            tldr = tldr.text

        article = self.find_between(item_str, '<body>', '</body>')
        article = article.replace('\n', '').replace('\r', '')
        article = re.sub("\s\s+", " ", article)

        return {
            'id': story_id,
            'created': created,
            'updated': '',
            'images': [],
            'headline': '',
            'located': located,
            'tldr': tldr,
            'article': article,
            'videos': [],
            'facts': []
        }


        #
        # item_new = fromstring(item_str)
        # print(item_str)
        #
        #
        # ns = {
        #     'html': "http://www.w3.org/1999/xhtml",
        #     'ns0': "http://iptc.org/std/nar/2006-10-01",
        #     'ns1': "http://www.reuters.com/ns/2003/08/content"
        # }

        # i = item.find('{http://iptc.org/std/nar/2006-10-01}newsMessage')
        # print(i)


        # print(soup.findAll('newsMessage'))
        # for article_xml in soup.find_all(XML_NAMESPACE + 'headline'):
        #     print(article_xml.text)


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
