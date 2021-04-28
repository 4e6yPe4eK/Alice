from data import db_session
from data.day import Day
from data.timetable import Timetable
from data.teacher import Teacher


def get_day(id):
    db_sess = db_session.create_session()
    day = db_sess.query(Day).get(id)
    result = day.id, day.name
    return result


def get_teacher(id):
    db_sess = db_session.create_session()
    teacher = db_sess.query(Teacher).get(id)
    result = teacher.id, teacher.name
    return result


def get_schedule_itcube(id):
    db_sess = db_session.create_session()
    times = db_sess.query(Timetable).filter(Timetable.name == id).all()
    result = []
    for time in times:
        result.append((time.id, time.name, time.day, time.time, time.room, time.teacher, time.group))
    return result
