#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from datetime import datetime

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def home():
    return "<h1>Bakery GET-POST-PATCH-DELETE API</h1>"


@app.route("/bakeries")
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries, 200)


@app.route("/bakeries/<int:id>", methods=["GET", "PATCH", "DELETE"])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()

    if not bakery:
        return make_response({"message": "Bakery not found"}, 404)

    if request.method == "GET":
        return make_response(bakery.to_dict(), 200)

    elif request.method == "PATCH":
        # Handle both form data and JSON
        data = request.get_json() if request.is_json else request.form

        if "name" in data:
            bakery.name = data["name"]
        if "address" in data:
            bakery.address = data["address"]
        db.session.commit()
        return make_response(bakery.to_dict(), 200)

    elif request.method == "DELETE":
        db.session.delete(bakery)
        db.session.commit()
        return make_response({"message": "Bakery deleted"}, 200)


@app.route("/baked_goods/by_price")
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [bg.to_dict() for bg in baked_goods_by_price]
    return make_response(baked_goods_by_price_serialized, 200)


@app.route("/baked_goods/most_expensive")
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response(most_expensive_serialized, 200)


@app.route("/baked_goods", methods=["GET", "POST"])
def baked_goods():
    if request.method == "GET":
        baked_goods = BakedGood.query.all()
        response = [baked_good.to_dict() for baked_good in baked_goods]
        return make_response(response, 200)
    elif request.method == "POST":
        # Handle both form data and JSON
        data = request.get_json() if request.is_json else request.form
        new_baked_good = BakedGood(
            name=data.get("name"),
            price=data.get("price"),
            created_at=data.get("created_at", datetime.now()),  # Handle timestamps
            updated_at=data.get("updated_at", datetime.now()),
            bakery_id=data.get("bakery_id"),
        )
        db.session.add(new_baked_good)
        db.session.commit()
        return make_response(new_baked_good.to_dict(), 201)


@app.route("/baked_goods/<int:id>", methods=["DELETE"])
def delete_baked_good(id):
    baked_good = BakedGood.query.filter_by(id=id).first()

    if not baked_good:
        return make_response({"message": "Baked good not found"}, 404)

    db.session.delete(baked_good)
    db.session.commit()
    return make_response({"message": "Baked good deleted"}, 200)


if __name__ == "__main__":
    app.run(port=5555, debug=True)