from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    datetime_created = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=8))
    datetime_deleted = db.Column(db.DateTime, default=None, nullable=True)

    def to_map(self):
        return {
            "id": self.id,
            "datetime_created": self.datetime_created,
            "datetime_deleted": self.datetime_deleted
        }

class Branch(BaseModel):
    __tablename__ = "branch"
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship("User", backref="branch", lazy=True)
    units = db.relationship("Unit", backref="branch", lazy=True)
    categories = db.relationship("Category", backref="branch", lazy=True)
    ingredients = db.relationship("Ingredients", backref="branch", lazy=True)
    products = db.relationship("Products", backref="branch", lazy=True)

    def to_map(self):
        branch_data = super().to_map()
        branch_data["name"] = self.name
        return branch_data

class User(BaseModel):
    __tablename__ = "user"
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    user_type = db.Column(db.String(100), nullable=False)

    def to_map(self):
        user_data = super().to_map()
        user_data["username"] = self.username
        user_data["password"] = self.password
        user_data["fullname"] = self.fullname
        user_data["branch_id"] = self.branch_id
        user_data["user_type"] = self.user_type
        return user_data

class Unit(BaseModel):
    __tablename__ = "unit"
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def to_map(self):
        unit_data = super().to_map()
        unit_data["branch_id"] = self.branch_id
        unit_data["name"] = self.name
        return unit_data

class Category(BaseModel):
    __tablename__ = "category"
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def to_map(self):
        category_data = super().to_map()
        category_data["branch_id"] = self.branch_id
        category_data["name"] = self.name
        return category_data

class Ingredients(BaseModel):
    __tablename__ = "ingredients"
    name = db.Column(db.String(100), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey("unit.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    tolerance = db.Column(db.Float, nullable=False)

    def to_map(self):
        ingredients_data = super().to_map()
        ingredients_data["name"] = self.name
        ingredients_data["unit_id"] = self.unit_id
        ingredients_data["category_id"] = self.category_id
        ingredients_data["branch_id"] = self.branch_id
        ingredients_data["tolerance"] = self.tolerance
        return ingredients_data

class Products(BaseModel):
    __tablename__ = "products"
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def to_map(self):
        products_data = super().to_map()
        products_data["branch_id"] = self.branch_id
        products_data["name"] = self.name
        products_data["price"] = self.price
        return products_data

class ProductIngredient(BaseModel):
    __tablename__ = "product_ingredient"
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    def to_map(self):
        product_ingredient_data = super().to_map()
        product_ingredient_data["product_id"] = self.product_id
        product_ingredient_data["ingredient_id"] = self.ingredient_id
        product_ingredient_data["quantity"] = self.quantity
        return product_ingredient_data

class Inventory(BaseModel):
    __tablename__ = "inventory"
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    is_starting = db.Column(db.Boolean, nullable=False)

    def to_map(self):
        inventory_data = super().to_map()
        inventory_data["branch_id"] = self.branch_id
        inventory_data["is_starting"] = self.is_starting
        return inventory_data

class InventoryItem(BaseModel):
    __tablename__ = "inventory_item"
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey("inventory.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    remarks = db.Column(db.String(100), nullable=True)

    def to_map(self):
        inventory_item_data = super().to_map()
        inventory_item_data["ingredient_id"] = self.ingredient_id
        inventory_item_data["inventory_id"] = self.inventory_id
        inventory_item_data["quantity"] = self.quantity
        inventory_item_data["remarks"] = self.remarks
        return inventory_item_data

class InventoryTransaction(BaseModel):
    __tablename__ = "inventory_transaction"
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    transaction_type = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    remarks = db.Column(db.String(100), nullable=False)

    def to_map(self):
        inventory_transaction_data = super().to_map()
        inventory_transaction_data["branch_id"] = self.branch_id
        inventory_transaction_data["ingredient_id"] = self.ingredient_id
        inventory_transaction_data["user_id"] = self.user_id
        inventory_transaction_data["transaction_type"] = self.transaction_type
        inventory_transaction_data["quantity"] = self.quantity
        inventory_transaction_data["remarks"] = self.remarks
        return inventory_transaction_data

class Sales(BaseModel):
    __tablename__ = "sales"
    branch_id = db.Column(db.Integer, db.ForeignKey("branch.id"), nullable=False)
    items = db.relationship("SalesItem", backref="sales", lazy=True)

    def to_map(self):
        sales_data = super().to_map()
        sales_data["branch_id"] = self.branch_id
        sales_data["items"] = [item.to_map() for item in self.items]
        return sales_data

class SalesItem(BaseModel):
    __tablename__ = "sales_item"
    sales_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def to_map(self):
        sales_item_data = super().to_map()
        sales_item_data["sales_id"] = self.sales_id
        sales_item_data["product_id"] = self.product_id
        sales_item_data["quantity"] = self.quantity
        return sales_item_data
