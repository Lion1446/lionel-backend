import datetime
from datetime import timedelta
from sqlalchemy import func
from flask import Blueprint
from flask import make_response, request
import json
from models import Ingredients, Products, ProductIngredient, Category, Unit
from constants import *
from models import db


products_blueprint = Blueprint('products_blueprint', __name__)

@products_blueprint.route('/products', methods = ["POST", "GET", "DELETE", "PATCH"])
def products():
    try:
        if request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                product_query = Products.query.filter(Products.branch_id == request_data["branch_id"], Products.name == request_data["name"]).first()
                if product_query:
                    resp = make_response({"status": 400, "remarks": "Product already exists."})
                else:
                    product = Products(
                        branch_id = request_data["branch_id"],
                        name = request_data["name"],
                        price = request_data["price"],
                        category_id = request_data["category_id"]
                    )
                    db.session.add(product)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
        elif request.method == "GET":
            branch_id = request.args.get('branch_id')
            if branch_id is None:
                resp = make_response({"status": 400, "remarks": "Missing branch id in the query string"})
            else:
                products = Products.query.filter(Products.branch_id == branch_id).all()
                if products is None:
                    resp = make_response({"status": 200, "remarks": "Store doesn't have products yet."})
                else:
                    response_body = {}
                    response_body["products"] = []
                    for product in products:
                        response_body["products"].append(product.to_map())
                        category = Category.query.get(product.category_id)
                        response_body["products"]["category"] = category.name
                    response_body["status"] = 200
                    response_body["remarks"] = "Success"
                    resp = make_response(response_body)
        elif request.method == "DELETE":
            id = request.args.get('id')
            product = Products.query.get(id)
            if product is None:
                resp = make_response({"status": 404, "remarks": "Product not found"})
            else:
                product_ingredients = ProductIngredient.query.filter(ProductIngredient.product_id == id).all()
                if product_ingredients is not None:
                    for pi in product_ingredients:
                        db.session.delete(pi)
                db.session.delete(product)
                db.session.commit()
                resp = make_response({"status": 200, "remarks": "Success"})
        elif request.method == "PATCH":
            id = request.args.get('id')
            product = Products.query.get(id)
            if product is None:
                resp = make_response({"status": 404, "remarks": "Product not found"})
            else:
                request_data = request.data
                request_data = json.loads(request_data.decode('utf-8')) 
                if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                    product.name = request_data["name"]
                    product.price = request_data["price"]
                    product.category_id = request_data["category_id"]
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
                else:
                    resp = make_response({"status": 403, "remarks": "Access denied"})
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@products_blueprint.route('/product_ingredients', methods=['POST', 'GET', 'DELETE', 'PATCH'])
def product_ingredients():
    try:
        if request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                product_ingredient_query = ProductIngredient.query.filter(ProductIngredient.ingredient_id == request_data["ingredient_id"], ProductIngredient.product_id == request_data["product_id"]).first()
                if product_ingredient_query:
                    resp = make_response({"status": 400, "remarks": "Ingredient in this product already exists."})
                else:
                    product_ingredient = ProductIngredient(
                        ingredient_id=request_data["ingredient_id"],
                        product_id=request_data["product_id"],
                        quantity=request_data["quantity"]
                    )
                    db.session.add(product_ingredient)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
        elif request.method == "GET":
            product_id = request.args.get('product_id')
            if product_id is None:
                resp = make_response({"status": 400, "remarks": "Missing id in the query string"})
            else:
                product_ingredients = ProductIngredient.query.filter(ProductIngredient.product_id == product_id).all()
                if product_ingredients is None:
                    resp = make_response({"status": 404, "remarks": "No ingredients found for this product."})
                else:
                    response_body = {}
                    response_body["product_ingredients"] = []
                    for pi in product_ingredients:
                        ingredient = Ingredients.query.filter(Ingredients.id == pi.ingredient_id).first()
                        product = Products.query.filter(Products.id == pi.product_id).first()
                        category = Category.query.get(product.category_id)
                        unit = Unit.query.get(ingredient.unit_id)
                        product_ingredient_detail = pi.to_map()
                        product_ingredient_detail["category"] = category.name
                        product_ingredient_detail["ingredient_details"] = ingredient.to_map()
                        product_ingredient_detail["ingredient_details"]["unit"] = unit.name
                        response_body["product_ingredients"].append(product_ingredient_detail)
                    response_body["status"] = 200
                    response_body["remarks"] = "Success"
                    resp = make_response(response_body)
        elif request.method == "DELETE":
            id = request.args.get('id')
            pi = ProductIngredient.query.get(id)
            if pi is None:
                resp = make_response({"status": 404, "remarks": "Product Ingredient not found"})
            else:
                db.session.delete(pi)
                db.session.commit()
                resp = make_response({"status": 200, "remarks": "Product Ingredient deleted successfully"})
        elif request.method == "PATCH":
            id = request.args.get('id')
            pi = ProductIngredient.query.get(id)
            if pi is None:
                resp = make_response({"status": 404, "remarks": "Product Ingredient not found"})
            else:
                request_data = request.data
                request_data = json.loads(request_data.decode('utf-8')) 
                if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                    pi.quantity = request_data["quantity"]
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Product Ingredient updated successfully"})
                else:
                    resp = make_response({"status": 403, "remarks": "Access denied"})
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp