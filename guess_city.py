from flask import Flask, request
import os
from random import shuffle

TOKEN = 'cabb4c5b-70a8-4826-8857-4e12fc11fe7b'
HELP = '''Игра "Угадай город"
Ваша задача угадать город показанный на картинке'''

app = Flask(__name__)


@app.route('/post', methods=['POST'])
def main():
    response = make_response(request.json)
    return response


def make_response(json):
    session_id = json['session']['session_id']
    response = {
        "response": {
            "text": "Угадай город",
            "end_session": False,
        },
        'version': json['version']
    }
    add_buttons(response)
    if json['request']['type'] == 'ButtonPressed':
        if 'payload' in json['request']:
            if 'city' in json['request']['payload']:
                response['response'][
                    'text'] = f"А вот и {json['request']['payload']['city'].capitalize()}"
                return response
    if json['request']['original_utterance'].lower() == 'помощь':
        response['response']['text'] = HELP
        return response
    if json['session']['new']:
        init_cites_for_user(session_id)
    cites_names = get_cites(json)
    city = None
    if sessions[session_id]['city_to_country']:
        countries_names = get_countries(json)
        current_country_name = cites[sessions[session_id]['cites'][0]]['country']
        if countries_names:
            if current_country_name in countries_names:
                city_index = sessions[session_id]['cites'][0]
                city = cites[city_index]['name']
                sessions[session_id]['city_to_country'] = False
                del sessions[session_id]['cites'][0]
    if cites_names:
        current_city_name = cites[sessions[session_id]['cites'][0]]['name']
        if current_city_name in cites_names:
            sessions[session_id]['city_to_country'] = True
            response['response']['text'] = 'Верно! А в какой стране этот город?'
            return response
    if sessions[session_id]['cites']:
        response['response']['card'] = cites[sessions[session_id]['cites'][0]]['card']
        if city:
            response['response']['card']['title'] = 'Совершенно верно! А что это за город?'
        elif not city and not json['session']['new']:
            response['response']['card']['title'] = 'Попробуй еще разок!'
        else:
            response['response']['card']['title'] = 'Что это за город?'
    else:
        response['response']['end_session'] = True
        response['response']['text'] = 'Игра окончена'
        init_cites_for_user(session_id)
    add_buttons(response, city)
    return response


def init_cites_for_user(session_id):
    cites_current_user = list(range(len(cites)))
    shuffle(cites_current_user)
    sessions[session_id] = {
        'cites': cites_current_user,
        'city_to_country': False
    }


def add_buttons(json, city=None):
    json['response']['buttons'] = [
        {
            "title": "Помощь",
            "hide": True,
        }
    ]
    if city:
        json['response']['buttons'].append({
            'title': city.capitalize(),
            'hide': True,
            'url': f'https://yandex.ru/maps/?mode=search&text={city}',
            'payload': {
                'answer': False,
                'city': city
            }
        })


def get_cites(json):
    entities = json['request']['nlu']['entities']
    if entities:
        geos = list(filter(lambda obj: obj['type'] == 'YANDEX.GEO', entities))
        if not geos:
            return None
        cites = list(filter(lambda geo: 'city' in geo['value'], geos))
        if not cites:
            return None
        cites_names = list(map(lambda city: city['value']['city'], cites))
        return cites_names
    else:
        return None


def get_countries(json):
    entities = json['request']['nlu']['entities']
    if entities:
        geos = list(filter(lambda obj: obj['type'] == 'YANDEX.GEO', entities))
        if not geos:
            return None
        countries = list(filter(lambda geo: 'country' in geo['value'], geos))
        if not cites:
            return None
        countries_names = list(map(lambda city: city['value']['country'], countries))
        return countries_names
    else:
        return None


cites = [
    {
        'name': 'нью-йорк',
        'country': 'сша',
        'card': {
            "type": "BigImage",
            "image_id": '1652229/a79a1b730ae0added55d',
        }
    },
    {
        'name': 'нью-йорк',
        'country': 'сша',
        'card': {
            "type": "BigImage",
            "image_id": '997614/9196dc45ef4cc24d8c1e',
        }
    },

    {
        'name': 'москва',
        'country': 'россия',
        'card': {
            "type": "BigImage",
            "image_id": '1030494/dc7bf2531a7fa0e6142e',
        }
    },
    {
        'name': 'москва',
        'country': 'россия',
        'card': {
            "type": "BigImage",
            "image_id": '1030494/63723b5a8991ee585527',
        }
    },

    {
        'name': 'париж',
        'country': 'франция',
        'card': {
            "type": "BigImage",
            "image_id": '1656841/384c34a050c8a40053c8',
        }
    },
    {
        'name': 'париж',
        'country': 'франция',
        'card': {
            "type": "BigImage",
            "image_id": '213044/4de02007eb98fb6c6181',
        }
    },
]

sessions = {

}

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
