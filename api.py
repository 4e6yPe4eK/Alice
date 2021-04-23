from flask import Flask, request
import logging
from const import *
from database import get_day, get_teacher, get_schedule_itcube
import datetime
import json
from requests import get

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='example.log')

sessionStorage = {}


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
                "����������",
                "���������� � ������������",
                "�������"
            ],
            'step': START,
            'direction': None
        }
        res['response']['text'] = '������! � ���� ���������� ���� ���������� ��� ���������� � ������������ ItCube'
        res['response']['buttons'] = get_suggests(user_id)
        return
    if sessionStorage[user_id]['step'] == START:
        if '��������' in text:
            sessionStorage[user_id] = {
                'suggests': [str(x) for x in range(1, 17)],
                'step': SCHEDULE,
                'direction': None
            }
            res['response']['text'] = '1. ���������������� �� Python, ������.�����.\n' \
                                      '2. IT ����� SAMSUNG.\n' \
                                      '3. VR/AR - ����������.\n' \
                                      '4. ������������ � ������� ������.\n' \
                                      '5. ������ ����������� � ������.\n' \
                                      '6. �������������.\n' \
                                      '7. ��������� �����������������.\n' \
                                      '8. ������ ������������� ���������.\n' \
                                      '9. ������ ���������������� � �������� �����������.\n' \
                                      '10. ���������������.\n' \
                                      '11. ���������������� ��-��������.\n' \
                                      '12. ��������.\n' \
                                      '13. ����������.\n' \
                                      '14. ���������� ����.\n' \
                                      '15. ��������� �����.\n' \
                                      '16. �������.\n' \
                                      '������ �����������:'
            res['response']['buttons'] = get_suggests(user_id)
        elif ('������' in text or '������' in text) and '�������' in text:
            sessionStorage[user_id] = {
                'suggests': [str(x) for x in range(1, 10)],
                'step': INFORMATION,
                'direction': None
            }
            res['response']['text'] = '1. ������.�����.\n' \
                                      '2. IT ����� SAMSUNG.\n' \
                                      '3. VR/AR - ����������.\n' \
                                      '4. ������������ � ������� ������.\n' \
                                      '5. ������ ����������� � ������.\n' \
                                      '6. �������������.\n' \
                                      '7. ��������� �����������������.\n' \
                                      '8. ������ ������������� ���������.\n' \
                                      '9. ������ ���������������� � �������� �����������.\n' \
                                      '������ �����������:'
            res['response']['buttons'] = get_suggests(user_id)
        elif '�����' in text:
            res['response']['text'] = '������, ����������!\n�� ������ ������ ������� ���� �� ��� ������ ��� ���������?'
            sessionStorage[user_id]['step'] = EVENTS
            sessionStorage[user_id]['suggests'] = [
                '��� ������',
                '��������� ������'
            ]
            res['response']['buttons'] = get_suggests(user_id)
        else:
            res['response']['text'] = '� �� ����������, �������, ����������.'
            res['response']['buttons'] = get_suggests(user_id)
    elif sessionStorage[user_id]['step'] == SCHEDULE:
        num = get_number(req)
        if num and 0 < num < 17:
            sessionStorage[user_id] = {
                'suggests': [
                    "���������"
                ],
                'step': ANSWERED_ALL,
                'direction': None
            }
            text_all = []
            for num_num in DATABASE_TO_CODE[num]:
                for i in get_schedule_itcube(num_num):
                    text = ''
                    text += get_day(i[2])[1] + '\n'
                    text += '����� ������: ' + str(i[3]) + '\n'
                    text += '�������: ' + str(i[4]) + '\n'
                    text += '�������: ' + get_teacher(i[5])[1] + '\n'
                    text_all.append((i[2], text))
            text_all.sort()
            text_all = [f'{x + 1}. ' + text_all[x][1] for x in range(len(text_all))]
            res['response']['text'] = '\n'.join(text_all)
            res['response']['buttons'] = get_suggests(user_id)
        else:
            res['response']['text'] = '� �� ����������, �������, ����������.'
            res['response']['buttons'] = get_suggests(user_id)
    elif sessionStorage[user_id]['step'] == INFORMATION:
        num = get_number(req)
        if num and 0 < num < 10:
            sessionStorage[user_id] = {
                'suggests': [
                    "������������ �������",
                    "���������"
                ],
                'step': ANSWERED_INFORMATION,
                'direction': num
            }
            res['response']['text'] = DIRECTION_INFORMATION_TEXT[num]
            res['response']['buttons'] = get_suggests(user_id)
        else:
            res['response']['text'] = '� �� ����������, �������, ����������.'
            res['response']['buttons'] = get_suggests(user_id)
    elif sessionStorage[user_id]['step'] == ANSWERED_INFORMATION:
        if '�������' in text or '���' in text:
            if sessionStorage[user_id]['direction']:
                res['response']['text'] = DIRECTION_INFORMATION_AGE[sessionStorage[user_id]['direction']]
            else:
                res['response']['text'] = '� ���� ������!'
            sessionStorage[user_id] = {
                'suggests': [
                    "������������ �������",
                    "���������"
                ],
                'step': ANSWERED_INFORMATION,
                'direction': sessionStorage[user_id]['direction']
            }
            res['response']['buttons'] = get_suggests(user_id)
        else:
            sessionStorage[user_id] = {
                'suggests': [
                    "����������",
                    "���������� � ������������",
                    "�������"
                ],
                'step': START,
                'direction': None
            }
            res['response']['text'] = '��� ��� �� ������ ������?'
            res['response']['buttons'] = get_suggests(user_id)
    elif sessionStorage[user_id]['step'] == ANSWERED_ALL:
        sessionStorage[user_id] = {
            'suggests': [
                "����������",
                "���������� � ������������",
                "�������"
            ],
            'step': START,
            'direction': None
        }
        res['response']['text'] = '��� ��� �� ������ ������?'
        res['response']['buttons'] = get_suggests(user_id)
    elif sessionStorage[user_id]['step'] == EVENTS:
        if '��' in text:
            dt = datetime.datetime.today()
            d1 = dt - datetime.timedelta(days=dt.weekday())
            d2 = d1 + datetime.timedelta(days=7)
            response = api.date_request(d1, d2)
            if response == 0:
                res['response']['text'] = '�� ���� ������ � ���� ��� ������� �������'
            else:
                text123 = '�� ���� ������ � ���� �������� ��������� �������:\n'
                for i in response['events']:
                    k1 = f'������� {i["Etitle_of_event"]}\n'
                    k1 += f'������: {i["Edate_of_start_event"]}\n'
                    k1 += f'�����: {i["Edate_of_finish_event"]}\n'
                    k1 += i['Edescription'] + '\n'
                    text123 += k1
                res['response']['text'] = text123
            sessionStorage[user_id]['suggests'] = [
                '���������'
            ]
            sessionStorage[user_id]['step'] = ANSWERED_ALL
            res['response']['buttons'] = get_suggests(user_id)
        elif '����' in text:
            dt = datetime.datetime.today()
            d1 = dt - datetime.timedelta(days=dt.weekday())
            d1 += datetime.timedelta(days=7)
            d2 = d1 + datetime.timedelta(days=7)
            response = api.date_request(d1, d2)
            if response == 0:
                res['response']['text'] = '�� ��������� ������ � ���� ��� ������� �������'
            else:
                text123 = '�� ��������� ������ � ���� �������� ��������� �������:\n'
                for i in response['events']:
                    k1 = f'������� {i["Etitle_of_event"]}\n'
                    k1 += f'������: {i["Edate_of_start_event"]}\n'
                    k1 += f'�����: {i["Edate_of_finish_event"]}\n'
                    k1 += i['Edescription'] + '\n'
                    text123 += k1
                res['response']['text'] = text123
            sessionStorage[user_id]['suggests'] = [
                '���������'
            ]
            sessionStorage[user_id]['step'] = ANSWERED_ALL
            res['response']['buttons'] = get_suggests(user_id)
        else:
            res['response']['text'] = '� �� ����������, �������, ����������.'
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