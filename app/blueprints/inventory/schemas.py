
from app.extensions import ma
from app.models import Inventory
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(min=1, max=100))
    price = fields.Float(required=True)
    stock = fields.Int(required=True)

    service_item = fields.Nested('ServiceItemSchema', exclude=('item_id',))
    
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