import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class GmailUser(Base):
    __tablename__ = 'gmailuser'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(220), nullable=False)


class GunsmodelsName(Base):
    __tablename__ = 'gunsmodelsname'
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    user_id = Column(Integer, ForeignKey('gmailuser.id'))
    user = relationship(GmailUser, backref="gunsmodelsname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class GunsName(Base):
    __tablename__ = 'gunsname1'
    id = Column(Integer, primary_key=True)
    gunsname = Column(String(350), nullable=False)
    launchyear = Column(String(150))
    killrating = Column(String(150))
    gunstype = Column(String(150))
    price = Column(String(10))
    date = Column(DateTime, nullable=False)
    gunsmodelsnameid = Column(Integer, ForeignKey('gunsmodelsname.id'))
    gunsmodelsname = relationship(
        GunsmodelsName, backref=backref('gunsname', cascade='all, delete'))
    gmailuser_id = Column(Integer, ForeignKey('gmailuser.id'))
    gmailuser = relationship(GmailUser, backref="gunsname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'gunsname': self. gunsname,
            'launchyear': self. launchyear,
            'killrating': self. killrating,
            'price': self. price,
            'gunstype': self. gunstype,
            'date': self. date,
            'id': self. id
        }

engin = create_engine('sqlite:///guns.db')
Base.metadata.create_all(engin)
