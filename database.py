import sqlite3
con = sqlite3.connect("alice/db.db")


def get_day(id):
    cur = con.cursor()
    result = cur.execute("SELECT * FROM days WHERE id = ?;", (id, )).fetchone()
    return result


def get_teacher(id):
    cur = con.cursor()
    result = cur.execute("SELECT * FROM teachers WHERE id = ?;", (id, )).fetchone()
    return result


def get_schedule_itcube(id):
    cur = con.cursor()
    if id == 'all':
        result = cur.execute("SELECT * FROM timetable;").fetchall()
    else:
        result = cur.execute("SELECT * FROM timetable WHERE name = ? ORDER BY day ASC;", (id, )).fetchall()
    return result