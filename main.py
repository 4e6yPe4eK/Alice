from flask import Flask, request
import logging
from const import *
from database import get_day, get_teacher, get_schedule_itcube
import datetime
import json
from requests import get
from data import db_session

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='example.log')

sessionStorage = {}
db_session.global_init('alice/db/db.db')


class EventApi:
    def __init__(self, apikey):
        self.apikey = apikey

    def request(self, k: str = ''):
        try:
            result = get(f'http://localhost:8090/api/key={self.apikey}/events/' + k).json()
            if type(result) == str and 'not found' in result:
                return 0
            return result
        except Exception:
            return 0

    def id_request(self, n: int):
        return self.request(str(n))

    def get_all(self):
        return self.request()

    def date_request(self, d1: datetime, d2: datetime):
        m = d1.strftime('%Y/%m/%d')
        m += ':'
        m += d2.strftime('%Y/%m/%d')
        return self.request(m)


api = EventApi('***')


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    text = req["request"]['original_utterance'].lower()

    if req['session']['new']:

        sessionStorage[user_id] = {
            'suggests': [
                "Расписание",
                "Информация о направлениях",
                "События",
                "Немного о кубе"
            ],
            'step': START,
            'direction': None
        }
        res['response']['text'] = 'Привет! Я могу рассказать тебе расписание или информацию о направлениях ItCube'
        res['response']['buttons'] = get_suggests(user_id)
        return
    if sessionStorage[user_id]['step'] == START:
        if 'расписан' in text:
            sessionStorage[user_id] = {
                'suggests': [str(x) for x in range(1, 17)],
                'step': SCHEDULE,
                'direction': None
            }
            res['response']['text'] = '1. Программирование на Python, Яндекс.Лицей.\n' \
                                      '2. IT школа SAMSUNG.\n' \
                                      '3. VR/AR - разработка.\n' \
                                      '4. Кибергигиена и большие данные.\n' \
                                      '5. Основы алгоритмики и логики.\n' \
                                      '6. Робототехника.\n' \
                                      '7. Системное администрирование.\n' \
                                      '8. Основы искуственного интелекта.\n' \
                                      '9. Основы программирования и цифровой грамотности.\n' \
                                      '10. Медиатехнологии.\n' \
                                      '11. Программиравание Си-подобные.\n' \
                                      '12. Нанодети.\n' \
                                      '13. Математика.\n' \
                                      '14. Английский язык.\n' \
                                      '15. Проектная школа.\n' \
                                      '16. Биодети.\n' \
                                      'Выбери направление:'
            res['response']['buttons'] = get_suggests(user_id)
        elif ('описан' in text or 'информ' in text) and 'направл' in text:
            sessionStorage[user_id] = {
                'suggests': [str(x) for x in range(1, 10)],
                'step': INFORMATION,
                'direction': None
            }
            res['response']['text'] = '1. Яндекс.Лицей.\n' \
                                      '2. IT школа SAMSUNG.\n' \
                                      '3. VR/AR - разработка.\n' \
                                      '4. Кибергигиена и большие данные.\n' \
                                      '5. Основы алгоритмики и логики.\n' \
                                      '6. Робототехника.\n' \
                                      '7. Системное администрирование.\n' \
                                      '8. Основы искуственного интелекта.\n' \
                                      '9. Основы программирования и цифровой грамотности.\n' \
                                      'Выбери направление:'
            res['response']['buttons'] = get_suggests(user_id)
        elif 'событ' in text:
            res['response']['text'] = 'Привет, Крокозябра!\nТы хочешь узнать события куба за эту неделю или следующую?'
            sessionStorage[user_id]['step'] = EVENTS
            sessionStorage[user_id]['suggests'] = [
                'Эта неделя',
                'Следующая неделя'
            ]
            res['response']['buttons'] = get_suggests(user_id)
        elif 'куб' in text or 'cube' in text:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['image_id'] = '1652229/ffcfdf180ebb9b7ccc18'
            res['response']['card']['title'] = ITCUBE_INFO
            res['response']['text'] = ITCUBE_INFO
            sessionStorage[user_id]['suggests'] = [
                'Вернуться'
            ]
            res['response']['buttons'] = get_suggests(user_id)
            sessionStorage[user_id]['step'] = ANSWERED_ALL
        else:
            res['response']['text'] = 'Я не расслышала, повтори, пожалуйста.'
            res['response']['buttons'] = get_suggests(user_id)

    elif sessionStorage[user_id]['step'] == SCHEDULE:
        num = get_number(req)
        if num and 0 < num < 17:
            sessionStorage[user_id] = {
                'suggests': [
                    "Вернуться"
                ],
                'step': ANSWERED_ALL,
                'direction': None
            }
            text_all = []
            for num_num in DATABASE_TO_CODE[num]:
                for i in get_schedule_itcube(num_num):
                    text = ''
                    text += get_day(i[2])[1] + '\n'
                    text += 'Время начала: ' + str(i[3]) + '\n'
                    text += 'Кабинет: ' + str(i[4]) + '\n'
                    text += 'Учитель: ' + get_teacher(i[5])[1] + '\n'
                    text_all.append((i[2], text))
            text_all.sort()
            text_all = [f'{x + 1}. ' + text_all[x][1] for x in range(len(text_all))]
            res['response']['text'] = '\n'.join(text_all)
            res['response']['buttons'] = get_suggests(user_id)
        else:
            res['response']['text'] = 'Я не расслышала, повтори, пожалуйста.'
            res['response']['buttons'] = get_suggests(user_id)
    elif sessionStorage[user_id]['step'] == INFORMATION:
        num = get_number(req)
        if num and 0 < num < 10:
            sessionStorage[user_id] = {
                'suggests': [
                    "Рекомедуемый возраст",
                    "Вернуться"
                ],
                'step': ANSWERED_INFORMATION,
                'direction': num
            }
            res['response']['text'] = DIRECTION_INFORMATION_TEXT[num]
            res['response']['buttons'] = get_suggests(user_id)
        else:
            res['response']['text'] = 'Я не расслышала, повтори, пожалуйста.'
            res['response']['buttons'] = get_suggests(user_id)
    elif sessionStorage[user_id]['step'] == ANSWERED_INFORMATION:
        if 'возраст' in text or 'лет' in text:
            if sessionStorage[user_id]['direction']:
                res['response']['text'] = DIRECTION_INFORMATION_AGE[sessionStorage[user_id]['direction']]
            else:
                res['response']['text'] = 'У меня ошибка!'
            sessionStorage[user_id] = {
                'suggests': [
                    "Рекомедуемый возраст",
                    "Вернуться"
                ],
                'step': ANSWERED_INFORMATION,
                'direction': sessionStorage[user_id]['direction']
            }
            res['response']['buttons'] = get_suggests(user_id)
        else:
            sessionStorage[user_id] = {
                'suggests': [
                    "Расписание",
                    "Информация о направлениях",
                    "События",
                    "Немного о кубе"
                ],
                'step': START,
                'direction': None
            }
            res['response']['text'] = 'Что ещё вы хотите узнать?'
            res['response']['buttons'] = get_suggests(user_id)
    elif sessionStorage[user_id]['step'] == ANSWERED_ALL:
        sessionStorage[user_id] = {
            'suggests': [
                "Расписание",
                "Информация о направлениях",
                "События",
                "Немного о кубе"
            ],
            'step': START,
            'direction': None
        }
        res['response']['text'] = 'Что ещё вы хотите узнать?'
        res['response']['buttons'] = get_suggests(user_id)
    elif sessionStorage[user_id]['step'] == EVENTS:
        if 'эт' in text:
            dt = datetime.datetime.today()
            d1 = dt - datetime.timedelta(days=dt.weekday())
            d2 = d1 + datetime.timedelta(days=7)
            response = api.date_request(d1, d2)
            if response == 0:
                res['response']['text'] = 'На этой неделе в кубе нет никаких событий'
            else:
                text123 = 'На этой неделе в кубе проходят следующие события:\n'
                for i in response['events']:
                    k1 = f'Событие {i["Etitle_of_event"]}\n'
                    k1 += f'Начало: {i["Edate_of_start_event"]}\n'
                    k1 += f'Конец: {i["Edate_of_finish_event"]}\n'
                    k1 += i['Edescription'] + '\n'
                    text123 += k1
                res['response']['text'] = text123
            sessionStorage[user_id]['suggests'] = [
                'Вернуться'
            ]
            sessionStorage[user_id]['step'] = ANSWERED_ALL
            res['response']['buttons'] = get_suggests(user_id)
        elif 'след' in text:
            dt = datetime.datetime.today()
            d1 = dt - datetime.timedelta(days=dt.weekday())
            d1 += datetime.timedelta(days=7)
            d2 = d1 + datetime.timedelta(days=7)
            response = api.date_request(d1, d2)
            if response == 0:
                res['response']['text'] = 'На следующей неделе в кубе нет никаких событий'
            else:
                text123 = 'На следующей неделе в кубе проходят следующие события:\n'
                for i in response['events']:
                    k1 = f'Событие {i["Etitle_of_event"]}\n'
                    k1 += f'Начало: {i["Edate_of_start_event"]}\n'
                    k1 += f'Конец: {i["Edate_of_finish_event"]}\n'
                    k1 += i['Edescription'] + '\n'
                    text123 += k1
                res['response']['text'] = text123
            sessionStorage[user_id]['suggests'] = [
                'Вернуться'
            ]
            sessionStorage[user_id]['step'] = ANSWERED_ALL
            res['response']['buttons'] = get_suggests(user_id)
        else:
            res['response']['text'] = 'Я не расслышала, повтори, пожалуйста.'
            res['response']['buttons'] = get_suggests(user_id)

def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]

    return suggests


def get_number(req):
    for i in req["request"]['command'].split():
        if i.isdigit():
            return int(i)
    if req['request']['nlu']['intents']["direction"]["slots"]["piece"]["type"] == "ItCube":
        return int(req['request']['nlu']['intents']["direction"]["slots"]["piece"]["value"])


if __name__ == '__main__':
    app.run()