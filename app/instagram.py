import json

import requests


class InstagramApi:

    @staticmethod
    def get_images(keyword):
        keyword = keyword.replace(' ', '').replace('.', '')
        response = requests.get(f'https://www.instagram.com/explore/tags/{keyword}/?__a=1')
        if response.status_code == 200:
            content = json.loads(response.content)
            nodes = content['tag']['top_posts']['nodes']
            if len(nodes) > 0:
                return nodes[0]['thumbnail_src']
            return 'Invalid Instagram JSON structure'
        return 'Invalid Response'
