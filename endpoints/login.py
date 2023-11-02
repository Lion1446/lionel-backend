from flask import Blueprint
from flask import make_response, request
import json
from models import User, Branch
from constants import *

login_blueprint = Blueprint('login_blueprint', __name__)

# curl -X POST -d "{\"username\": \"ayame_pa\", \"password\": \"superadmin1446\"}" -H "Content-Type: application/json" http://127.0.0.1:5000/login
@login_blueprint.route('/login', methods = ["POST"])
def login():
    try:
        request_data = request.data
        request_data = json.loads(request_data.decode('utf-8')) 
        user = User.query.filter(User.username == request_data["username"], User.password == request_data["password"]).first()
        if user:
            branch = Branch.query.filter(Branch.id == user.branch_id).first()
            response_body = {}
            response_body["status"] = 200
            response_body["remarks"] = "Success"
            response_body["branch"] = branch.to_map()
            response_body["user"] = user.to_map()
            if user.user_type == 1:
                response_body["auth_token"] = ADMIN_AUTH_TOKEN
            else:
                response_body["auth_token"] = AUTH_TOKEN
        else:
            response_body = {}
            response_body["status"] = 401
            response_body["remarks"] = "Invalid credentials"
        resp = make_response(response_body)
    except Exception as e:
        print("Error is:", e)
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp