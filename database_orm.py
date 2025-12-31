from peewee import *

DATABASE_FILENAME = 'user_settings.db'
db = SqliteDatabase(DATABASE_FILENAME)


class BaseModel(Model):
    # Creating a base class so all the children now know about the database we're working with
    class Meta:
        database = db    # This model uses the "user_settings.db" database. Mandatory attribute

# A database table
class Favourites(BaseModel):
    city_name = CharField()  # column on the table

class Alerts(BaseModel):
    city_name = CharField()
    min_temp_alert = FloatField(default=None)
    max_temp_alert = FloatField(default=None)
    # ...

# In order to start using the models, its necessary to create the tables.
# This is a one-time operation and can be done quickly using the interactive interpreter
def initialize_db(db_filename):
    def create_tables():
        with db:
            db.create_tables([Favourites, Alerts])

    try:
        with open(db_filename) as file:
            if not file: create_tables()
    except FileNotFoundError:
        create_tables()

initialize_db(DATABASE_FILENAME)
