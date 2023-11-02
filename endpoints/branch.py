from flask import Blueprint
from flask import make_response, request
import json
from models import Branch
from constants import *
from models import db

branch_blueprint = Blueprint('branch_blueprint', __name__)


# curl -X POST -d "{\"admin_auth_token\": \"WvNM3UJL2kHZQ1ewI7RzGxVh0n8o6YKS\", \"name\": \"Ayame - SM Seaside\"}" -H "Content-Type: application/json" http://127.0.0.1:5000/branch
@branch_blueprint.route('/branch', methods = ["POST", "GET", "PATCH"])
def branch():
    try:
        if request.method == "POST":
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["admin_auth_token"] == ADMIN_AUTH_TOKEN:
                query = Branch.query.filter(Branch.name == request_data["name"]).first()
                if query:
                    resp = make_response({"status": 400, "remarks": "Branch already exists."})
                else:
                    instance = Branch(
                        name = request_data["name"],
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
                instance = Branch.query.filter(Branch.id == id).first()
                response_body = instance.to_map()
                response_body["status"] = 200
                response_body["remarks"] = "Success"
                resp = make_response(response_body)
        elif request.method == "PATCH":
            id = request.args.get('id')
            if id is None:
                resp = make_response({"status": 400, "remarks": "Missing id in the query string"})
            branch = Branch. query.get(id)      
            if branch is None:
                return make_response({"status": 404, "remarks": "Branch not found"})
            request_data = request.data
            request_data = json.loads(request_data.decode('utf-8')) 
            if request_data["auth_token"] in [AUTH_TOKEN, ADMIN_AUTH_TOKEN]:   
                branch.name = request_data["name"]
                db.session.commit()
                return make_response({"status": 200, "remarks": "Success"})
            else:
                return make_response({"status": 403, "remarks": "Access denied"})

           
            
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@branch_blueprint.route('/branches', methods=["GET"])
def branches():
    try:
        branch_instances = Branch.query.all()
        branches = []
        for instance in branch_instances:
            branch = instance.to_map()
            branches.append(branch)
        response_body = {}
        response_body["status"] = 200
        response_body["remarks"] = "Success"
        response_body["branches"] = branches
        resp = make_response(response_body)
    except Exception as e:
        print(e)
        resp = make_response({"status": 500, "remarks": f"Internal server error: {e}"})
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp