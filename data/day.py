import sqlalchemy
from .db_session import SqlAlchemyBase


class Day(SqlAlchemyBase):
    __tablename__ = 'days'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)
    # start_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    # finish_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    name = sqlalchemy.Column(sqlalchemy.String)