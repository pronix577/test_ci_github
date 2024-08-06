import factory
import factory.fuzzy as fuzzy
import random

from ..app.main import db
from ..app.models import Client, Parking


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    credit_card = fuzzy.FuzzyChoice(choices=[None, 'any cards'])
    car_number = fuzzy.FuzzyText(length=10)


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker('address')
    opened = fuzzy.FuzzyChoice(choices=[True, False])
    count_places = fuzzy.FuzzyInteger(low=5, high=10)
    count_available_places = factory.LazyAttribute(lambda x: random.randint(0, 5))
