import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json

# database_filename = "database.db"
# project_dir = os.path.dirname(os.path.abspath(__file__))
# database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))


database_name = 'coffeeCafe'
database_path = 'postgres://{}@{}/{}'.format('nishmajain', 'localhost:5432', database_name)


db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to have multiple verisons of a database
'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

'''
Drink
a persistent drink entity, extends the base SQLAlchemy Model
'''
class Drink(db.Model):

    __tablename__ = 'drink'
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    recipe =  Column(String, nullable=False)

    # Autoincrementing, unique primary key
    #id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)

    # String Title
    #title = Column(String(80), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string, 'parts':number}]
    # recipe =  Column(String(180), nullable=False)

    '''
    short()
        short form representation of the Drink model
    '''
    def short(self):
        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }

    '''
    long()
        long form representation of the Drink model
    '''
    def long(self):
        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }

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
        db.session.delete(self)
        db.session.commit()

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

    def format(self):
        #print(self.recipe)
        return {
            'id': self.id,
            'title': self.title,
            'recipe': self.recipe
        }    

    def __repr__(self):
        return json.dumps(self.short())