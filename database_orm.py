from peewee import SqliteDatabase, Model, CharField, FloatField 

DATABASE_FILENAME = 'user_settings.db'
db = SqliteDatabase(DATABASE_FILENAME)


class BaseModel(Model):
    # Creating a base class so all the children now know about the database we're working with
    class Meta:
        database = db    # This model uses the "user_settings.db" database. Mandatory attribute.


class Alert(BaseModel):  # A database table
    city_name = CharField()  # or Location object?      # column on the table
    min_temp = FloatField(default=-273.15)
    max_temp = FloatField(default=1000.0)
    # min_wind_speed = FloatField(default=0.0)
    # max_wind_speed = FloatField(default=100.0)
    # min_precipitation = FloatField(default=0.0)
    # max_precipitation = FloatField(default=1000.0)
    # min_humidity = FloatField(default=0.0)
    # max_humidity = FloatField(default=100.0)
    # min_pressure = FloatField(default=0.0)
    # max_pressure = FloatField(default=2000.0)
    # ...

# In order to start using the models, its necessary to create the tables.
# This is a one-time operation and can be done quickly using the interactive interpreter
def initialize_db(db_filename):
    def create_tables():
        with db:
            db.create_tables([Alert])

    try:
        with open(db_filename) as file:
            if not file: create_tables()
    except FileNotFoundError:
        create_tables()

initialize_db(DATABASE_FILENAME)
