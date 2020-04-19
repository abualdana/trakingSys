# !/usr/bin/env python

import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(Integer)


class Location(Base):
    __tablename__ = 'location'

    lat = Column(String(50), nullable=False)
    lng = Column(String(50), nullable=False)
    date = Column(DateTime)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data.
        return {
            'id': self.id,
            'lat': self.lat,
            'lng': self.lng,
            'date': self.date,
            'user_id': self.user_id,
        }



engine = create_engine('sqlite:///dataset.db')
Base.metadata.create_all(engine)
