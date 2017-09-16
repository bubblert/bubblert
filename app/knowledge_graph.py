import json
import urllib
import requests
import urllib.parse

from settings import KNOWLEDGE_SEARCH_API_TOKEN

SEARCH_URL = 'https://kgsearch.googleapis.com/v1/entities:search'

if not KNOWLEDGE_SEARCH_API_TOKEN:
    raise Exception('set KNOWLEDGE_SEARCH_API_TOKEN token')

def get_facts_for_keyword(query):
    """
    get factual knowledge for a given query

    :param query:
    :return:
    """
    params = {
        'query': query,
        'limit': 10,
        'indent': True,
        'key': KNOWLEDGE_SEARCH_API_TOKEN,
    }

    r = requests.get(SEARCH_URL, params=params)
    if r.status_code not in [200, 201]:
        return None

    data = r.json()
    # - id
    # - title
    # - content
    # - link
    # - pictures

    INIT_SCORE = 200
    facts = []

    for element in data['itemListElement']:
        score = element['resultScore']
        if score > INIT_SCORE and element['result'].get('description') \
                and element['result'].get('detailedDescription'):
            detail = element['result'].get('detailedDescription')
            image = element['result'].get('image')
            img_url = image.get('url') if image else None

            fact = {
                'id': element.get('result').get('@id'),
                'title': element['result']['name'],
                'description': element['result'].get('description'),
                'body': detail.get('articleBody'),
                'bodyUrl': detail.get('url'),
                'image_url': img_url
            }
            facts.append(fact)

    return facts


if __name__ == '__main__':
    get_facts_for_keyword('hi')
