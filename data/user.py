from sqlalchemy import Column, Integer, String
from sqlalchemy import orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    login = Column(String, unique=True, index=True)
    email = Column(String, nullable=True, unique=True)
    hashed_password = Column(String)
    points = Column(Integer, default=0)
    guessed_count = Column(Integer, default=0)

    current_word = Column(String, default='-')
    current_try = Column(Integer, default=0)
    entered_words = Column(String)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
