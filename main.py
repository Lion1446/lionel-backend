from flask import Flask, make_response
from models import *
from constants import *
from endpoints.login import login_blueprint
from endpoints.branch import branch_blueprint
from endpoints.user import user_blueprint
from endpoints.ingredient import ingredient_blueprint
from endpoints.products import products_blueprint
from endpoints.inventory import inventory_blueprint
from endpoints.sales import sales_blueprint
# from endpoints.audit import audit_blueprint


## ======================= STARTUPS =================================

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] =\
#         'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://dbuser:Heleadsm3!2#@172.104.175.65:5231/lionel'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()  

app.register_blueprint(login_blueprint)
app.register_blueprint(branch_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(ingredient_blueprint)
app.register_blueprint(products_blueprint)
app.register_blueprint(inventory_blueprint)
app.register_blueprint(sales_blueprint)
# app.register_blueprint(audit_blueprint)


## ======================= ENDPOINTS =================================

@app.route('/')
def index():
    return make_response({"status": 200, "remarks": "Backend connected"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)