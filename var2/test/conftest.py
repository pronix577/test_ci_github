import pytest

from ..app.main import create_app
from ..app.models import Client, Parking, db as _db


@pytest.fixture
def app():
    _app = create_app()
    _app.config['TESTING'] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///prod.db"

    with _app.app_context():
        _db.create_all()
        clients = Client(
            name='name',
            surname='surname',
            credit_card='credit_card',
            car_number='car_number'
        )
        parking = Parking(
            address='address',
            opened=True,
            count_places=5,
            count_available_places=3
        )
        _db.session.add(clients)
        _db.session.add(parking)
        _db.session.commit()

        yield _app
        _db.session.close()
        _db.drop_all()


@pytest.fixture
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
