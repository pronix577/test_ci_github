import datetime

from flask import Flask, jsonify, request

from .models import Client, ClientParking, Parking, db


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///prod.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    @app.before_request
    def before_request_func():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route("/clients", methods=["GET"])
    def get_clients():
        clients = db.session.query(Client).all()
        clients_list = [c.to_json() for c in clients]
        return jsonify(clients_list), 200

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client_for_id(client_id):
        client = db.session.query(Client).filter(Client.id == client_id).one()
        return jsonify(client.to_json()), 200

    @app.route("/clients", methods=["POST"])
    def create_client():
        name = request.form.get("name", type=str)
        surname = request.form.get("surname", type=str)
        credit_card = request.form.get("credit_card", type=str)
        car_number = request.form.get("car_number", type=str)

        new_client = Client(
            name=name,
            surname=surname,
            credit_card=credit_card,
            car_number=car_number
        )

        db.session.add(new_client)
        db.session.commit()

        return "ok", 201

    @app.route("/parking", methods=["POST"])
    def create_parking():
        address = request.form.get("address", type=str)
        opened = request.form.get("opened", type=bool)
        count_places = request.form.get("count_places", type=int)
        count_available_places = request.form.get(
            "count_available_places",
            type=int
        )

        new_parking = Parking(
            address=address,
            opened=opened,
            count_places=count_places,
            count_available_places=count_available_places,
        )

        db.session.add(new_parking)
        db.session.commit()

        return "ok", 201

    @app.route("/client_parking", methods=["POST"])
    def to_enter_parking():
        client_id = request.form.get("client_id", type=int)
        parking_id = request.form.get("parking_id", type=int)

        parking = db.session.get(Parking, parking_id)

        if parking.opened is False:
            return "Parking is close", 200

        if parking.count_available_places > 0:
            parking.count_available_places -= 1
        else:
            return "There are no available places", 200

        new_log = ClientParking(
            client_id=client_id,
            parking_id=parking_id,
            time_in=datetime.datetime.now(),
            time_out=None,
        )

        db.session.add(new_log)
        db.session.commit()

        return "ok", 201

    @app.route("/client_parking", methods=["DELETE"])
    def to_leave_parking():
        client_id = request.form.get("client_id", type=int)
        parking_id = request.form.get("parking_id", type=int)

        parking = db.session.get(Parking, parking_id)
        client = db.session.get(Client, client_id)

        logs = (
            db.session.query(ClientParking.id)
            .filter(ClientParking.client_id == client_id)
            .filter(ClientParking.time_out is None)
            .first()
        )

        log = db.session.get(ClientParking, logs)

        time_out = datetime.datetime.now()
        log.time_out = time_out

        parking.count_available_places += 1

        db.session.commit()

        cards = client.credit_card

        if not cards:
            return "Карты нет! Штраф 5000р!", 200

        different = log.time_out - log.time_in
        different_h = different.seconds / 3600
        cost = different_h * 50

        return f"С вашей карты {cards} спишется {cost} рублей", 200

    return app


if __name__ == "__main__":
    application = create_app()
    application.run()
    # some
