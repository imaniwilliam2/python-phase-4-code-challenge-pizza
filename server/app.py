#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Restaurants(Resource):

    def get(self):
        restaurants = [restaurant.to_dict(only=('id', 'address', 'name')) for restaurant in Restaurant.query.all()]
        return make_response(restaurants, 200)
    
api.add_resource(Restaurants, '/restaurants')

class RestaurantsByID(Resource):
    
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if restaurant:
            response = restaurant.to_dict(rules=('-restaurantpizzas.restaurant', '-restaurantpizzas.pizza.restaurantpizzas'))
            response['restaurant_pizzas'] = response.pop('restaurantpizzas')
            return make_response(response, 200)
        else:
            response = make_response(
                {"error": "Restaurant not found"},
                404
            )
            return response
        
    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)

        if(restaurant):
            db.session.delete(restaurant)
            db.session.commit()
            response = {}
            return make_response(response, 204)
        else:
            response = {
                "error": "Restaurant not found"
            }
            return make_response(response, 404)
        
api.add_resource(RestaurantsByID, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict(only=('id', 'ingredients', 'name')) for pizza in Pizza.query.all()]
        return make_response(pizzas, 200)
    
api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):

    def post(self):
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=request.json.get('price'),
                pizza_id=request.json.get('pizza_id'),
                restaurant_id=request.json.get('restaurant_id')
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            response = new_restaurant_pizza.to_dict(rules=('-restaurant.restaurantpizzas', '-pizza.restaurantpizzas'))
            return make_response(response, 201)
        except:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(response_body, 400)
    
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')






@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)
