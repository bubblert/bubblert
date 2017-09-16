import urllib
from urllib.request import urlopen
import time
import logging
from xml.etree.ElementTree import ElementTree, fromstring, tostring

from requests import HTTPError

from settings import REUTERS_PASSWORD, REUTERS_USERNAME

from bs4 import BeautifulSoup
import re

import json

AUTH_URL = "https://commerce.reuters.com/rmd/rest/xml/"
SERVICE_URL_JSON = "http://rmb.reuters.com/rmd/rest/json/"
SERVICE_URL_XML = "http://rmb.reuters.com/rmd/rest/xml/"
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

    def _call_string(self, method, args={}, auth=False, xml=False):
        if auth:
            root_url = AUTH_URL
        else:
            root_url = SERVICE_URL_XML if xml else SERVICE_URL_JSON
            args['token'] = self.authToken

        url = root_url + method + '?' + urllib.parse.urlencode(args)
        logging.debug('> ' + url)
        resp = urlopen(url, timeout=10)
        rawd = resp.read()
        return rawd.decode('utf-8')

    def _call_xml(self, method, args={}):
        s = self._call_string(method, args, False, xml=True)
        return fromstring(s)

    def _call_json(self, method, args={}):
        j = self._call_string(method, args, False)
        return json.loads(j)

    def get_channels(self):
        return [
            'BEQ259',
            'FES376',
            'STK567',
            'Wbz248'
        ]

    def recent_news(self, channel):
        return self._call_xml('items',
                              {'channel': channel,
                               'maxAge': '120m',
                               'mediaType': 'T'})

    def get_story(self, story_id):
        args = {}
        args['id'] = story_id
        try:
            item = self._call_json('item', args)
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
            'videos': videos
            # 'audio': []
        }

    def get_story_highlight(self, item_id):

        try:
            item_str = self._call_string('item', {'id': item_id}, xml=True)
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
