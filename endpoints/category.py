from flask import Blueprint, make_response, request
from constants import *
from models import Category, db

category_blueprint = Blueprint('category_blueprint', __name__)

@category_blueprint.route('/category', methods=["POST", "GET", "PATCH", "DELETE"])
def category():
    try:
        if request.method == "POST":
            request_data = request.get_json()
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                instance = Category.query.filter(Category.name == request_data["name"], Category.branch_id == request_data["branch_id"]).first()
                if instance:
                    resp = make_response({"status": 400, "remarks": "Category already exists."})
                else:
                    instance = Category(
                        name=request_data["name"],
                        branch_id=request_data["branch_id"]
                    )
                    db.session.add(instance)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
        elif request.method == "GET":
            id = request.args.get('id')
            if id is None:
                categories = Category.query.all()
                response_body = [category.to_map() for category in categories]
                resp = make_response({"status": 200, "remarks": "Success", "categories": response_body})
            else:
                instance = Category.query.filter(Category.id == id).first()
                if instance is None:
                    resp = make_response({"status": 404, "remarks": "Category does not exist."})
                else:
                    response_body = instance.to_map()
                    response_body["status"] = 200
                    response_body["remarks"] = "Success"
                    resp = make_response(response_body)
        elif request.method == "PATCH":
            request_data = request.get_json()
            id = request.args.get('id')
            if id is None:
                resp = make_response({"status": 400, "remarks": "Missing id in the request body"})
            else:
                instance = Category.query.filter(Category.id == id).first()
                if instance is None:
                    resp = make_response({"status": 404, "remarks": "Category does not exist."})
                else:
                    if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                        instance.name = request_data["name"]
                        db.session.commit()
                        resp = make_response({"status": 200, "remarks": "Success"})
                    else:
                        resp = make_response({"status": 403, "remarks": "Access denied"})
        elif request.method == "DELETE":
            id = request.args.get('id')
            instance = Category.query.filter(Category.id == id).first()
            if instance is None:
                resp = make_response({"status": 404, "remarks": "Category does not exist."})
            else:
                db.session.delete(instance)
                db.session.commit()
                resp = make_response({"status": 200, "remarks": "Success"})
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp