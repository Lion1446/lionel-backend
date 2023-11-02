from flask import Blueprint
from flask import make_response, request
import json
from models import Ingredients, ProductIngredient, InventoryItem, InventoryTransaction, Category, Unit
from constants import *
from models import db

ingredient_blueprint = Blueprint('ingredient_blueprint', __name__)


@ingredient_blueprint.route('/ingredients', methods = ["GET"])
def ingredients():
    try:
        branch_id = request.args.get('branch_id')
        if branch_id is None:
            resp = make_response({"status": 400, "remarks": "Missing branch id in the query string"})
        else:
            instances = Ingredients.query.filter(Ingredients.branch_id == branch_id).all()
            if len(instances) == 0:
                resp = make_response({"status": 404, "remarks": "Store does not have ingredients."})
            else:
                response_body = {}
                response_body["ingredients"] = []
                for instance in instances:
                    ingredient_body = instance.to_map()
                    category = Category.query.get(instance.category_id)
                    unit = Unit.query.get(instance.unit_id)
                    ingredient_body["category"] = category.name
                    ingredient_body["unit"] = unit.name
                    response_body["ingredients"].append(ingredient_body)
                response_body["status"] = 200
                response_body["remarks"] = "Success"
                resp = make_response(response_body)
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": "Internal server error"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


# curl -X POST -d "{\"admin_auth_token\": \"WvNM3UJL2kHZQ1ewI7RzGxVh0n8o6YKS\", \"name\": \"Ayame - SM Seaside\"}" -H "Content-Type: application/json" http://127.0.0.1:5000/branch
@ingredient_blueprint.route('/ingredient', methods = ["POST", "GET", "PATCH", "DELETE"])
def ingredient():
    try:
        if request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                query = Ingredients.query.filter(
                    Ingredients.name == request_data["name"],
                    Ingredients.unit_id == request_data["unit_id"],
                    Ingredients.branch_id == request_data["branch_id"],
                    Ingredients.tolerance == request_data["tolerance"],
                    Ingredients.category_id == request_data["category_id"],
                    ).all()
                if query:
                    resp = make_response({"status": 400, "remarks": "Ingredient already exists."})
                else:
                    instance = Ingredients(
                        name = request_data["name"],
                        unit_id = request_data["unit_id"],
                        branch_id = request_data["branch_id"],
                        tolerance = request_data["tolerance"],
                        category_id = request_data["category_id"]
                    )
                    db.session.add(instance)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
        elif request.method == "GET":
            id = request.args.get('id')
            if id is None:
                resp = make_response({"status": 400, "remarks": "Missing id in the query string"})
            else:
                instance = Ingredients.query.filter(Ingredients.id == id).first()
                if instance is None:
                    resp = make_response({"status": 404, "remarks": "Ingredient does not exist."})
                else:
                    response_body = instance.to_map()
                    category = Category.query.get(instance.category_id)
                    unit = Unit.query.get(instance.unit_id)
                    response_body["category"] = category.name
                    response_body["unit"] = unit.name
                    response_body["status"] = 200
                    response_body["remarks"] = "Success"
                    resp = make_response(response_body)
        elif request.method == "PATCH":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                id = request.args.get('id')
                if id is None:
                    resp = make_response({"status": 400, "remarks": "Missing id in the request body"})
                else:
                    instance = Ingredients.query.filter(Ingredients.id == id).first()
                    if instance is None:
                        resp = make_response({"status": 404, "remarks": "Ingredient does not exist."})
                    else:
                        instance.name = request_data["name"]
                        instance.unit_id = request_data["unit_id"]
                        instance.tolerance = request_data["tolerance"]
                        instance.category_id = request_data["category_id"]
                        db.session.commit()
                        resp = make_response({"status": 200, "remarks": "Success"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
        elif request.method == "DELETE":
            id = request.args.get('id')
            instance = Ingredients.query.filter(Ingredients.id == id).first()
            if instance is None:
                resp = make_response({"status": 404, "remarks": "Ingredient does not exist."})
            else:
                pis = ProductIngredient.query.filter(ProductIngredient.ingredient_id == id).all()
                for pi in pis:
                    db.session.delete(pi)
                items = InventoryItem.query.filter(InventoryItem.ingredient_id == id).all()
                for item in items:
                    db.session.delete(item)
                transactions = InventoryTransaction.query.filter(InventoryTransaction.ingredient_id == id).all()
                for transaction in transactions:
                    db.session.delete(transaction)
                db.session.delete(instance)
                db.session.commit()
                resp = make_response({"status": 200, "remarks": "Success"})
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp