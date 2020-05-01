from flask import Flask, request
from flask_ngrok import run_with_ngrok

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
    if json['request']['original_utterance'].lower() == 'помощь':
        response = {
            "response": {
                "text": HELP,
                "end_session": False,
            },
            'version': json['version']
        }
        add_buttons(response)
        return response
    response = {
        "response": {
            "text": "Угадай город",
            "end_session": False,
        },
        'version': json['version']
    }
    if json['session']['new']:
        sessions[session_id] = {
            'current_count_city': 0
        }
    cites_names = get_cites(json)
    city_ok = False
    if cites_names:
        current_city_name = cites[sessions[session_id]['current_count_city']]['name']
        if current_city_name in cites_names:
            sessions[session_id]['current_count_city'] += 1
            city_ok = True
    try:
        response['response']['card'] = cites[sessions[session_id]['current_count_city']]['card']
        if city_ok:
            response['response']['card']['title'] = 'Совершенно верно! А что это за город?'
        else:
            response['response']['card']['title'] = 'Попробуй еще разок!'
    except IndexError:
        response['response']['end_session'] = True
        response['response']['text'] = 'Игра окончена'
        sessions[session_id] = {
            'current_count_city': 0
        }
    add_buttons(response)
    return response


def add_buttons(json):
    json['response']['buttons'] = [
        {
            "title": "Помощь",
            "hide": True,
        }
    ]


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


cites = [
    {
        'name': 'нью-йорк',
        'card': {
            "type": "BigImage",
            "image_id": '1652229/a79a1b730ae0added55d',
        }
    },
    {
        'name': 'нью-йорк',
        'card': {
            "type": "BigImage",
            "image_id": '997614/9196dc45ef4cc24d8c1e',
        }
    },

    {
        'name': 'москва',
        'card': {
            "type": "BigImage",
            "image_id": '1030494/dc7bf2531a7fa0e6142e',
        }
    },
    {
        'name': 'москва',
        'card': {
            "type": "BigImage",
            "image_id": '1030494/63723b5a8991ee585527',
        }
    },

    {
        'name': 'париж',
        'card': {
            "type": "BigImage",
            "image_id": '1656841/384c34a050c8a40053c8',
        }
    },
    {
        'name': 'париж',
        'card': {
            "type": "BigImage",
            "image_id": '213044/4de02007eb98fb6c6181',
        }
    },
]

sessions = {

}

app.config['DEBUG'] = True
run_with_ngrok(app)
app.run()
