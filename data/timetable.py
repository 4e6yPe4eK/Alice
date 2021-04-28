import sqlalchemy
from .db_session import SqlAlchemyBase


class Timetable(SqlAlchemyBase):
    __tablename__ = 'timetable'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.Integer,
                             sqlalchemy.ForeignKey('names.id'))

    day = sqlalchemy.Column(sqlalchemy.Integer,
                            sqlalchemy.ForeignKey('days.id'))

    time = sqlalchemy.Column(sqlalchemy.Time)

    room = sqlalchemy.Column(sqlalchemy.Integer)

    teacher = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('teachers.id'))

    group = sqlalchemy.Column(sqlalchemy.String)