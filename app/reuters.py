import urllib
from urllib.request import urlopen
import time
import logging
from xml.etree.ElementTree import ElementTree, fromstring, tostring
from settings import REUTERS_PASSWORD, REUTERS_USERNAME

from bs4 import BeautifulSoup
import re

import json

AUTH_URL = "https://commerce.reuters.com/rmd/rest/xml/"
SERVICE_URL = "http://rmb.reuters.com/rmd/rest/json/"
XML_NAMESPACE = 'http://iptc.org/std/nar/2006-10-01'
CONTENT_SERVE = 'http://content.reuters.com/auth-server/content/'


class Reuters:
    def __init__(self, username=REUTERS_USERNAME, password=REUTERS_PASSWORD):
        self.authToken = None

        tree = fromstring(self._call_string('login', {'username': username, 'password': password}, True))
        if tree.tag == 'authToken':
            self.authToken = tree.text
        else:
            raise Exception('unable to obtain authToken')

    def _get_auth_token_key_val(self):
        return 'token=' + self.authToken

    def _call_string(self, method, args={}, auth=False):
        if auth:
            root_url = AUTH_URL
        else:
            root_url = SERVICE_URL
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

    def get_story(self, story_id):
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
        videos = []
        for ass in item.get('associations'):
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
                    # TODO issues with picture url
                    pic = pic_meta[0]
                    uri = CONTENT_SERVE + story_id + '/' + pic.get('uri') + '?token=' + self.authToken
                    pictures.append(uri)

            if ass.get('type') == 'video':
                vid_meta = ass.get('renditions')
                if vid_meta:
                    vid = vid_meta[0]
                    uri = CONTENT_SERVE + story_id + '/' + vid.get('uri') + '?token=' + self.authToken
                    videos.append(uri)

        return {
            'id': story_id,
            'created': item.get('firstcreated'),
            'updated': None,
            'images': pictures,
            'headline': item.get('headline'),
            'located': item.get('located'),
            'tldr': intro,
            'article': story,
            'language': item.get('language'),
            'videos': videos,
            # 'audio': []
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