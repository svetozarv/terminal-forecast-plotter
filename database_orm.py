from peewee import CharField, FloatField, Model, SqliteDatabase

DATABASE_FILENAME = 'user_settings.db'
MIN_TEMP = -100  # in *C
MAX_TEMP = 100   # there are probably won't be higher temps (at least on Earth)
MIN_WINDSPEED = 0.0  # in m/s
MAX_WINDSPEED = 343.0
db = SqliteDatabase(DATABASE_FILENAME)


class BaseModel(Model):
    # Creating a base class so all the children now know about the database we're working with
    class Meta:
        database = db    # This model uses the "user_settings.db" database. Mandatory attribute.


class Favourite(BaseModel):  # A database table
    city_name = CharField()  # column on the table


class Alert(BaseModel):
    city_name = CharField()
    lat = FloatField()
    lon = FloatField()
    name = CharField(default="-", max_length=30)
    severity = CharField(default="INFO", max_length=20)   # either INFO, WARNING, DANGER or CRITICAL
    min_temp = FloatField(default=MIN_TEMP)
    max_temp = FloatField(default=MAX_TEMP)
    min_wind_speed = FloatField(default=MIN_WINDSPEED)
    max_wind_speed = FloatField(default=MAX_WINDSPEED)
    # min_precipitation = FloatField(default=0.0)
    # max_precipitation = FloatField(default=1000.0)
    # min_humidity = FloatField(default=0.0)
    # max_humidity = FloatField(default=100.0)
    # min_pressure = FloatField(default=0.0)
    # max_pressure = FloatField(default=2000.0)
    # ...
    # TODO: it is possible to add more alerts, although it's not supported yet
    # consider only ones that make sense


# In order to start using the models, its necessary to create the tables.
# This is a one-time operation and can be done quickly using the interactive interpreter
def initialize_db(db_filename):
    def create_tables():
        with db:
            db.create_tables([Alert, Favourite])

    try:
        with open(db_filename) as file:
            if not file:
                create_tables()
    except FileNotFoundError:
        create_tables()


initialize_db(DATABASE_FILENAME)
