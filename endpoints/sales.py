import datetime
import json
from flask import Blueprint, make_response, request, jsonify
from models import db, Sales, SalesItem, Products, ProductIngredient, InventoryTransaction
from sqlalchemy import func
from constants import AUTH_TOKEN, ADMIN_AUTH_TOKEN    

sales_blueprint = Blueprint('sales_blueprint', __name__)

@sales_blueprint.route('/sales', methods=["GET", "POST", "DELETE", "PATCH"])
def get_sales():
    try:
        if request.method == "GET":
            date = request.args.get('date')
            branch_id = request.args.get('branch_id')
            if date is None or branch_id is None:
                return make_response({"status": 400, "remarks": "Missing date or branch_id in the query string"})

            formatted_date = datetime.datetime.strptime(date, "%m/%d/%Y %H:%M:%S")
            sales_query = Sales.query.filter(func.DATE(Sales.datetime_created) == formatted_date.date(), Sales.branch_id == branch_id).first()
            
            if sales_query:
                sales_items = SalesItem.query.filter(SalesItem.sales_id == sales_query.id).all()
                response_body = {}
                response_body["sales_items"] = []
                for item in sales_items:
                    product = Products.query.get(item.product_id)
                    si = item.to_map()
                    si["name"] = product.name
                    response_body["sales_items"].append(si)
                response_body["status"] = 200
                response_body["remarks"] = "Success"
                return make_response(response_body)
            else:
                return make_response({"status": 404, "remarks": "No sales items found for this date and branch."})
        elif request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:   
                formatted_date = datetime.datetime.strptime(request_data["date"], "%m/%d/%Y %H:%M:%S")
                sales_query = Sales.query.filter(func.DATE(Sales.datetime_created) == formatted_date.date(), Sales.branch_id == request_data["branch_id"]).first()
                if sales_query:
                    sales_item_query = SalesItem.query.filter(SalesItem.product_id == request_data["product_id"]).first()
                    if sales_item_query:
                        sales_item_query.quantity = sales_item_query.quantity + request_data["quantity"]
                    else:
                        sales_item = SalesItem(product_id = request_data["product_id"], quantity = request_data["quantity"], sales_id = sales_query.id)
                        db.session.add(sales_item)
                    ## get product here and its ingredients
                    product = Products.query.get(request_data["product_id"])
                    product_ingredients = ProductIngredient.query.filter(ProductIngredient.product_id == product.id).all()
                    for product_ingredient in product_ingredients:
                        sale_transaction = InventoryTransaction(
                            branch_id = request_data["branch_id"],
                            ingredient_id = product_ingredient.ingredient_id,
                            user_id = request_data["user_id"],
                            transaction_type = "sale",
                            quantity = product_ingredient.quantity * request_data["quantity"] * -1,
                            remarks =  f"{product.name}: {request_data['quantity']} orders",
                        )
                        db.session.add(sale_transaction)
                    ## make a transaction of these ingredients
                    db.session.commit()
                    return make_response({"status": 200, "remarks": "Success"})
                else:
                    sales = Sales(datetime_created = formatted_date, branch_id = request_data["branch_id"])
                    db.session.add(sales)
                    db.session.commit()
                    sales_item = SalesItem(product_id = request_data["product_id"], quantity = request_data["quantity"], sales_id = sales.id)
                    db.session.add(sales_item)
                    ## get product here and its ingredients
                    product = Products.query.get(request_data["product_id"])
                    product_ingredients = ProductIngredient.query.filter(ProductIngredient.product_id == product.id).all()
                    for product_ingredient in product_ingredients:
                        sale_transaction = InventoryTransaction(
                            branch_id = request_data["branch_id"],
                            ingredient_id = product_ingredient.ingredient_id,
                            user_id = request_data["user_id"],
                            transaction_type = "sale",
                            quantity = product_ingredient.quantity * request_data["quantity"] * -1,
                            remarks = product.name,
                        )
                        db.session.add(sale_transaction)
                    ## make a transaction of these ingredients
                    db.session.commit()
                    return make_response({"status": 200, "remarks": "Success"})
            else:
                return make_response({"status": 403, "remarks": "Access denied"})
        elif request.method == "DELETE":
            sales_item_id = request.args.get('sales_item_id')
            sales_item = SalesItem.query.get(sales_item_id)

            if sales_item is None:
                return make_response({"status": 404, "remarks": "Sales item not found"})
            db.session.delete(sales_item)
            db.session.commit()
            return make_response({"status": 200, "remarks": "Success"})
        
        elif request.method == "PATCH":
            sales_item_id = request.args.get('sales_item_id')
            sales_item = SalesItem.query.get(sales_item_id)
            if sales_item is None:
                return make_response({"status": 404, "remarks": "Sales item not found"})
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:   
                sales_item.quantity = request_data["quantity"]
                db.session.commit()
                return make_response({"status": 200, "remarks": "Success"})
            else:
                return make_response({"status": 403, "remarks": "Access denied"})
    except Exception as e:
        print(e)
        return make_response({"status": 500, "remarks": f"Internal server error: {e}"})
