import pytest
from ..app.models import Client, Parking


def test_client(client) -> None:
    client_data = {'name': 'name2', 'surname': 'surname2',
                   'credit_card': 'credit_card2', 'car_number': 'car_number2'}
    resp = client.post('/clients', data=client_data)

    assert 'ok' in resp.data.decode()


def test_parking(client) -> None:
    parking_data = {'address': 'address3', 'opened': True,
                    'count_places': 10, 'count_available_places': 8}
    resp = client.post('/parking', data=parking_data)

    assert 'ok' in resp.data.decode()


@pytest.mark.parking
def test_client_parking_in(client, db) -> None:
    client_parking_data = {'client_id': 1, 'parking_id': 1}
    parking = db.session.get(Parking, 1)
    assert parking.opened is True
    before = parking.count_available_places
    resp = client.post('/client_parking', data=client_parking_data)
    after = parking.count_available_places
    assert after < before
    assert 'ok' in resp.data.decode()


@pytest.mark.parking
def test_client_parking_out(client, db) -> None:
    client_parking_data = {'client_id': 1, 'parking_id': 1}
    clients = db.session.get(Client, 1)
    parking = db.session.get(Parking, 1)
    client.post('/client_parking', data=client_parking_data)
    before = parking.count_available_places
    resp = client.delete('/client_parking', data=client_parking_data)
    after = parking.count_available_places
    assert after > before
    assert 'С вашей карты' in resp.data.decode()
    assert clients.credit_card is not None


@pytest.mark.parametrize("route", ["/clients", "/clients/1"])
def test_route_status(client, route):
    rv = client.get(route)
    assert rv.status_code == 200
