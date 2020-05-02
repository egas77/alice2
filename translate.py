from flask import Flask, request
import json
import requests
import os

app = Flask(__name__)

translator_api_address = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
translator_api_key = 'trnsl.1.1.20200417T091733Z.97641bc81ad39cac.15ef6a03e1675576f0dcf0857241fd7970db3564'

# Добавляем логирование в файл.
# Чтобы найти файл, перейдите на pythonwhere в раздел files,
# он лежит в корневой папке

sessionStorage = dict()


@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    return json.dumps(response)


def handle_dialog(res, req):
    if req['session']['new']:
        res['response']['text'] = 'Привет. Я бот переводчик. Отправь мне сообщение' \
                                  ' "Переведите (переведи) слово ...", и я отправлю тебе перевод'
        return
    try:
        word = req['request']['nlu']['tokens'][2]
        response = requests.post(translator_api_address, params={
            'key': translator_api_key,
            'text': word,
            'lang': 'en',
        })
        if response:
            result = response.json()['text'][0]
            res['response']['text'] = result
        else:
            res['response']['text'] = 'Не удалось перевести!'
    except IndexError as ex:
        res['response']['text'] = 'Не удалось перевести!'
    return


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
