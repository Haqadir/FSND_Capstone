import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_name = "stocks"
database_path = "postgresql://{}/{}".format('localhost:5432', database_name)

'''
** User **
ID  | USERNAME

** Account **
ACCOUNT_ID | ACCOUNT_NAME | USER_ID | INVEST_CADENCE | INVEST_AMT

** Portfolio **
PORTFOLIO_ID | ACCOUNT_ID | TICKR | PERCENT_SHARE
'''

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

class User(db.Model):
  __tablename__ = 'user'
  # Autoincrementing, unique primary key
  id = db.Column(Integer, primary_key=True)
  username = db.Column(String(80), unique=True)

  children = db.relationship("Account", back_populates="parent", cascade="all, delete" )
  '''
  insert()
      inserts a new model into a database
      the model must have a unique name
      the model must have a unique id or null id
      EXAMPLE
          drink = Drink(title=req_title, recipe=req_recipe)
          drink.insert()
  '''
  def insert(self):
      db.session.add(self)
      db.session.commit()

  '''
  delete()
      deletes a new model into a database
      the model must exist in the database
      EXAMPLE
          drink = Drink(title=req_title, recipe=req_recipe)
          drink.delete()
  '''
  def delete(self):
    try:
      db.session.delete(self)
      db.session.commit()
    except:
      db.session.rollback()

  '''
  update()
      updates a new model into a database
      the model must exist in the database
      EXAMPLE
          drink = Drink.query.filter(Drink.id == id).one_or_none()
          drink.title = 'Black Coffee'
          drink.update()
  '''
  def update(self):
      db.session.commit()

  def __repr__(self):
      return json.dumps(self.short())
      
class Account(db.Model):  
  __tablename__ = 'account'

  account_id = db.Column(Integer, primary_key=True)
  account_name = Column(String)
  user_id = db.Column(Integer, db.ForeignKey('user.id'))
  invest_cadence = Column(Integer)
  invest_amt = Column(Integer)

  parent = db.relationship("User", back_populates="children")
  children = db.relationship("Portfolio", back_populates="parent", cascade="all, delete" )


  def __init__(self, account_id,account_name,user_id,invest_cadence,invest_amt):
    self.account_name = account_name
    self.account_id = account_id
    self.user_id = user_id
    self.invest_cadence = invest_cadence
    self.invest_amt = invest_amt


class Portfolio(db.Model):  
  __tablename__ = 'portfolio'

  account_id = Column(Integer, db.ForeignKey('account.account_id'))
  portfolio_id = Column(String, primary_key=True)
  tickr = Column(String)
  percent_share = Column(Integer)

  parent = db.relationship("Account", back_populates="children")
  
  def __init__(self, account_id, portfolio_id, tickr, percent_share):
    self.account_id = account_id
    self.portfolio_id = portfolio_id
    self.tickr = tickr
    self.percent_share = percent_share

  def insert(self):
  
    db.session.add(self)
    db.session.commit()

  
  def update(self):
    db.session.commit()

  def delete(self):
    try:
      db.session.delete(self)
      db.session.commit()
    except:
      db.session.rollback()

  def format(self):
    return {
      'id': self.id,
      'question': self.question,
      'answer': self.answer,
      'category': self.category,
      'difficulty': self.difficulty
    }