import json
import urllib
from os import environ
from urllib.request import urlopen
import logging
from xml.etree.ElementTree import fromstring, tostring

import requests

from bs4 import BeautifulSoup
import re


class Reuters:
    def __init__(self):
        self.authToken = None

        tree = fromstring(self._call_string('login', {
            'username': environ.get('REUTERS_USERNAME'),
            'password': environ.get('REUTERS_PASSWORD')
        }, True))
        if tree.tag == 'authToken':
            self.authToken = tree.text
        else:
            raise Exception('unable to obtain authToken')

    def _call_string(self, method, args={}, auth=False):
        if auth:
            root_url = environ.get('AUTH_URL')
        else:
            root_url = environ.get('SERVICE_URL')
            args['token'] = self.authToken

        url = root_url + method + '?' + urllib.parse.urlencode(args)
        logging.debug('> ' + url)
        resp = urlopen(url, timeout=10)
        rawd = resp.read()
        return rawd.decode('utf-8')

    def call_xml(self, method, args={}):
        return fromstring(self._call_string(method, args, False))

    def call_json(self, method, args={}):
        j = self._call_string(method, args, False)
        return json.loads(j)

    def find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def get_story_json(self, story_id):
        args = {}
        args['id'] = story_id
        try:
            item = self.call_json('item', args)
        except urllib.error.HTTPError as e:
            logging.error(e)
            return None

        story = ''
        intro = ''
        pictures = []
        for ass in  item.get('associations'):
            if ass.get('type') == 'text':
                story = ass.get('body_xhtml')
                story = story.replace('\n', '').replace('\r', '')
                story = re.sub("\s\s+", " ", story)
                intro = ass.get('intro')

            if ass.get('type') == 'picture':
                uri = ''
                pic_meta = ass.get('renditions')
                if pic_meta:
                    # TODO choose picture with largest size
                    pic = pic_meta[0]
                    uri = pic.get('uri')




        return {
            'id': story_id,
            'created': item.get('firstcreated'),
            'updated': None,
            'images': [],
            'headline': item.get('headline'),
            'located': item.get('located'),
            'tldr': intro,
            'article': story,
            'language': item.get('language'),
            'videos': [],
            'audio': []
        }

    def get_story(self, story_id):
        args = {}
        args['id'] = story_id
        try:
            item = self.call_xml('item', args)
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
        tldr = None
        for t in soup.find_all('description', attrs={'role': 'descRole:intro'}):
            tldr = t.text

        imgs = []
        for img in soup.findAll('contentSet'):
            print(img.text)

        article = self.find_between(item_str, '<body>', '</body>')
        article = article.replace('\n', '').replace('\r', '')
        article = re.sub("\s\s+", " ", article)

        return {
            'id': story_id,
            'created': created,
            'updated': None,
            'images': [],
            'headline': headline,
            'located': located,
            'tldr': tldr,
            'article': article,
            'lang': 'en',
            'videos': []
        }


class ReutersPermid:
    @staticmethod
    def get_tags(text):
        response = requests.post('https://api.thomsonreuters.com/permid/calais',
                                 data=text.encode('utf-8'),
                                 headers={
                                     'Content-Type': 'text/raw',
                                     'Accept': 'application/json',
                                     'x-ag-access-token': f'{environ.get("PERMID_TOKEN")}',
                                     'x-calais-language': 'English',
                                     'outputFormat': 'application/json'
                                 })
        if response.status_code == 200:
            tags = []
            permid = json.loads(response.content)
            for key in permid.keys():
                current_permid = permid[key]
                if 'relevance' in current_permid and float(current_permid['relevance']) > 0:
                    tags.append(current_permid['name'])
            return tags
        return 'Invalid response'
