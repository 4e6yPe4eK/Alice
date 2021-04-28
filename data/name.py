import sqlalchemy
from .db_session import SqlAlchemyBase


class Name(SqlAlchemyBase):
    __tablename__ = 'names'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True,
                           autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String)