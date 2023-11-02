from flask import Blueprint
from flask import make_response, request
import json
from models import User, Branch
from constants import *
from models import db

user_blueprint = Blueprint('user_blueprint', __name__)

# curl -X POST -d "{\"admin_auth_token\": \"WvNM3UJL2kHZQ1ewI7RzGxVh0n8o6YKS\", \"username\": \"lionelle1446\", \"password\": \"lionelle123\", \"fullname\": \"Lionelle Diaz\", \"branch_id\": 1, \"is_admin\": false}" -H "Content-Type: application/json" http://127.0.0.1:5000/user
@user_blueprint.route('/user', methods=["POST", "GET", "PATCH"])
def user():
    try:
        if request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["admin_auth_token"] == ADMIN_AUTH_TOKEN:
                query = User.query.filter(
                    User.username == request_data["username"],
                    User.password == request_data["password"],
                    User.fullname == request_data["fullname"],
                    User.branch_id == request_data["branch_id"],
                    User.user_type == request_data["user_type"],
                    ).all()
                if query:
                    resp = make_response({"status": 400, "remarks": "User already exists."})
                else:
                    instance = User(
                        username = request_data["username"],
                        password = request_data["password"],
                        fullname = request_data["fullname"],
                        branch_id = request_data["branch_id"],
                        user_type = request_data["user_type"]
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
                instance = User.query.filter(User.id == id).first()
                response_body = instance.to_map()
                response_body["status"] = 200
                response_body["remarks"] = "Success"
                resp = make_response(response_body)
        elif request.method == "PATCH":
            id = request.args.get('id')
            if id is None:
                resp = make_response({"status": 400, "remarks": "Missing id in the query string"})
            user = User. query.get(id)      
            if user is None:
                return make_response({"status": 404, "remarks": "User not found"})
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] == ADMIN_AUTH_TOKEN:   
                user.password = request_data["password"]
                user.fullname = request_data["fullname"]
                user.branch_id = request_data["branch_id"]
                user.user_type = request_data["user_type"]
                db.session.commit()
                return make_response({"status": 200, "remarks": "Success"})
            else:
                return make_response({"status": 403, "remarks": "Access denied"})
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@user_blueprint.route('/users', methods=["GET"])
def users():
    try:
        user_instances = User.query.all()
        users = []
        for instance in user_instances:
            user = instance.to_map()
            branch = Branch.query.filter(Branch.id == user["branch_id"]).first()
            user["branch"] = branch.to_map()
            users.append(user)
        response_body = {}
        response_body["status"] = 200
        response_body["remarks"] = "Success"
        response_body["users"] = users
        resp = make_response(response_body)
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp