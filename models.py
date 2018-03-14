from database import Base
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
class dbArtists(Base):
    """
    Artists table
    """
    __tablename__ = 'artists'
    artistid=Column(Integer, primary_key=True, autoincrement=True)
    name=Column(Text,)

class dbUsers(Base):
    """
    Users table
    """
    __tablename__ = "users"
    userid = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text,)

class dbRatings(Base):
    """
    Ratings table
    """
    __tablename__ = 'ratings'
    ratingid = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, ForeignKey('users.userid'), nullable=False)
    artistid = Column(Integer, ForeignKey('artists.artistid'), nullable=False)
    rating = Column(Integer, nullable=False)

    users = relationship("dbUsers", foreign_keys=[userid])
    artists = relationship("dbArtists", foreign_keys=[artistid])
