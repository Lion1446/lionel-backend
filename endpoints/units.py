from flask import Blueprint, make_response, request
from constants import *
from models import Unit, db

unit_blueprint = Blueprint('unit_blueprint', __name__)
category_blueprint = Blueprint('category_blueprint', __name__)

@unit_blueprint.route('/unit', methods=["POST", "GET", "PATCH", "DELETE"])
def unit():
    try:
        if request.method == "POST":
            request_data = request.get_json()
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                instance = Unit.query.filter(Unit.name == request_data["name"], Unit.branch_id == request_data["branch_id"]).first()
                if instance:
                    resp = make_response({"status": 400, "remarks": "Ingredient already exists."})
                else:
                    instance = Unit(
                        name=request_data["name"],
                        branch_id=request_data["branch_id"]
                    )
                    db.session.add(instance)
                    db.session.commit()
                    resp = make_response({"status": 200, "remarks": "Success"})
            else:
                resp = make_response({"status": 403, "remarks": "Access denied"})
        elif request.method == "GET":
            branch_id = request.args.get('branch_id')
            if id is None:
                resp = make_response({"status": 400, "remarks": "Missing id in the request body"})
            else:
                instances = Unit.query.filter(Unit.branch_id == branch_id).all()
                units = []
                for instance in instances:
                    units.append(instance.to_map())
                resp = make_response({"status": 200, "remarks": "Success", "categories": units})
        elif request.method == "PATCH":
            request_data = request.get_json()
            id = request.args.get('id')
            if id is None:
                resp = make_response({"status": 400, "remarks": "Missing id in the request body"})
            else:
                instance = Unit.query.filter(Unit.id == id).first()
                if instance is None:
                    resp = make_response({"status": 404, "remarks": "Unit does not exist."})
                else:
                    if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:
                        instance.name = request_data["name"]
                        db.session.commit()
                        resp = make_response({"status": 200, "remarks": "Success"})
                    else:
                        resp = make_response({"status": 403, "remarks": "Access denied"})
        elif request.method == "DELETE":
            id = request.args.get('id')
            instance = Unit.query.filter(Unit.id == id).first()
            if instance is None:
                resp = make_response({"status": 404, "remarks": "Unit does not exist."})
            else:
                db.session.delete(instance)
                db.session.commit()
                resp = make_response({"status": 200, "remarks": "Success"})
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
