# import datetime
# import json
# from flask import Blueprint, make_response, request, jsonify
# from models import db, Sales, SalesItem, Products, Inventory, Item, Ingredients, ProductIngredient
# from sqlalchemy import func
# from constants import AUTH_TOKEN, ADMIN_AUTH_TOKEN

# audit_blueprint = Blueprint('audit_blueprint', __name__)

# @audit_blueprint.route('/audit', methods=["POST"])
# # get the date and branch to audit
# # the inventory for that branch at that particular date must be closed by checking if an entry exists where is_starting = False
# # the sales for that branch at that particular date must be encoded by checking if there is at least one sales item recorded
# # get all the ingredients in the closing inventory and account their consumed, expired, spoiled, and bad_orders
# # make a summary of used ingredients based on the sales of that day. Do it as follows:
#     # get all the products sold on that date at that particular branch
#     # for each product, get all the ingredients and multiply their serving quantities to the number of orders made on that product
#     # sum all these ingredient serving quantities as sales_ingredient_consumed
#     # for each ingredient, match it against the inventory ingredients and compute their differences
#     # the differences must be remarked based on the ingredient tolerance
# # the ingredients in inventory and sales must be returned as if they are cross-joined even if one record does not exists on the other.
# # heres an expected returned output of this endpoint
# # {
# #     "status": 200,
# #     "remarks": "Success",
# #     "audit": [
# #         {
# #             "ingredient_id": 1,
# #             "ingredient_name": "Mango",
# #             "ingredient_tolerance": 0,
# #             "inventory_consumed": 1000,
# #             "inventory_expired": 0,
# #             "inventory_spoiled": 0,
# #             "inventory_bad_order": 0,
# #             "sales_consumed": 1000,
# #             "unit_difference": 0,
# #             "remarks": "OK" 
# #         },
# #         ...
# #     ]
# # }

# def audit():
#     try:
#         request_data = request.data
#         request_data = json.loads(request_data.decode('utf-8')) 
#         if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:  
#             formatted_date = datetime.datetime.strptime(request_data['date'], "%m/%d/%Y %H:%M:%S")
#             closing_inventory = Inventory.query.filter(
#                 func.DATE(Inventory.datetime_created) == formatted_date.date(),
#                 Inventory.is_starting == False,
#                 Inventory.branch_id == request_data["branch_id"]
#                 ).first()
#             if closing_inventory is None:
#                 return make_response({"status": 404, "remarks": "Closing inventory for this date does not exist."})

#             sales = Sales.query.filter(func.DATE(Sales.datetime_created) == formatted_date.date(), Sales.branch_id == request_data["branch_id"]).first()
#             if sales is None:
#                 return make_response({"status": 404, "remarks": "Sales for this date does not exist."})

#             inventory_items = []
#             inventory_items_query = Item.query.filter(Item.inventory_id == closing_inventory.id).all()
#             for item in inventory_items_query:
#                 inventory_item = {}
#                 ingredient_query = Ingredients.query.filter(Ingredients.id == item.ingredient_id).first()
#                 inventory_item["ingredient_id"] = ingredient_query.id
#                 inventory_item["ingredient_name"] = ingredient_query.name
#                 inventory_item["ingredient_tolerance"] = ingredient_query.tolerance
#                 inventory_item["inventory_consumed"] = item.consumed
#                 inventory_item["inventory_expired"] = item.expired
#                 inventory_item["inventory_spoiled"] = item.spoiled
#                 inventory_item["inventory_bad_order"] = item.bad_order
#                 inventory_item["sales_consumed"] = 0
#                 inventory_item["unit_difference"] = 0
#                 inventory_item["remarks"] = None
#                 inventory_items.append(inventory_item)
            
#             sales_items_query = SalesItem.query.filter(SalesItem.sales_id == sales.id).all()
#             for sales_item in sales_items_query:
#                 product_query = Products.query.filter(Products.id == sales_item.product_id).first()
#                 product_ingredients_query = ProductIngredient.query.filter(ProductIngredient.product_id == product_query.id).all()
#                 for product_ingredient in product_ingredients_query:
#                     ingredient_query = Ingredients.query.filter(Ingredients.id == product_ingredient.ingredient_id).first()
#                     is_found = False
#                     for item in inventory_items:
#                         if item["ingredient_id"] == product_ingredient.ingredient_id:
#                             is_found = True
#                             item["sales_consumed"] = item["sales_consumed"] + (product_ingredient.quantity * sales_item.quantity)
#                     if is_found == False:
#                         inventory_items.append({
#                             "ingredient_id": product_ingredient.ingredient_id,
#                             "ingredient_name": ingredient_query.name,
#                             "ingredient_tolerance": ingredient_query.tolerance,
#                             "inventory_consumed": 0,
#                             "inventory_expired": 0,
#                             "inventory_spoiled": 0,
#                             "inventory_bad_order": 0,
#                             "sales_consumed": product_ingredient.quantity * sales_item.quantity,
#                             "unit_difference": 0,
#                             "remarks": None,
#                         })
#             for item in inventory_items:
#                 if item["sales_consumed"] != 0:
#                     item["unit_difference"] = item["sales_consumed"] - item["inventory_consumed"]
#                     if item["unit_difference"] > item["ingredient_tolerance"]:
#                         item["remarks"] = "underserved"
#                     elif item["unit_difference"] < -item["ingredient_tolerance"]:
#                         item["remarks"] = "overserved"
#                     else:
#                         item["remarks"] = "okay"

#             return make_response({
#                 "status": 200,
#                 "remarks": "Success",
#                 "audit": inventory_items,
#             })
                
#     except Exception as e:
#         resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
#     resp.headers['Access-Control-Allow-Origin'] = '*'
#     return resp
