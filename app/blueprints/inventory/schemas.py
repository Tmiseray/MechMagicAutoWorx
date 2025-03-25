
from app.models import Inventory, db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length


class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        include_relationships = True
        load_instance = True
        sqla_session = db.session

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(min=1, max=100))
    stock = fields.Int(required=True)
    price = fields.Float(required=True)

    service_items = fields.List(fields.Nested('ServiceItemSchema', only=('service_id', 'service', 'mechanic_tickets',)))
    
    @validates('name')
    def validate_name(self, value):
        if not value:
            raise ValidationError("Name is required.")
    
    @validates('price')
    def validate_price(self, value):
        if not value:
            raise ValidationError("Price is required.")
    
    @validates('stock')
    def validate_stock(self, value):
        if not value:
            raise ValidationError("Stock is required.")


inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)