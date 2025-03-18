
from app.extensions import ma
from app.models import ServiceItem
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class ServiceItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceItem
        include_relationships = True
        load_instance = True

    item_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=Length(min=1))

    inventory = fields.Nested('InventorySchema', exclude=('id',))

    @validates('quantity')
    def validate_quantity(self, value):
        if not value:
            raise ValidationError("Quantity is required.")
        if len(value) < 1:
            raise ValidationError("Quantity must be at least 1.")
        

service_item_schema = ServiceItemSchema()
service_items_schema = ServiceItemSchema(many=True)