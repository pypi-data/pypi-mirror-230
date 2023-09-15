from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

engine = create_engine('sqlite:////var/tmp/api_catalog.sqlite')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]
        
class Projects(Base, Serializer):
  __tablename__ = 'projects'

  id = Column(Integer, primary_key=True)
  username = Column(String, nullable=False)
  function_name = Column(String, nullable=False)
  function_params = Column(String, nullable=False)
  image_tag = Column(String, nullable=False)
  endpoint_url = Column(String, nullable=False)
  port = Column(String, nullable=False)
  help_message = Column(String, nullable=True)
  parameters = Column(String, nullable=True)

  def __init__(self, username, function_name, function_params, image_tag, endpoint_url, port, help_message = None, parameters = None):
    self.username = username
    self.function_name = function_name
    self.function_params = function_params
    self.image_tag = image_tag
    self.endpoint_url = endpoint_url
    self.port = port
    self.help_message = help_message
    self.parameters = parameters

  def serialize(self):
      d = Serializer.serialize(self)
      return d

Projects.__table__.create(bind=engine, checkfirst=True)