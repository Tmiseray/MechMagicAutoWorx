
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

    id = fields.Int(dump_only=True)
    item_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=Length(min=1))
    service_id = fields.Int(required=False)

    inventory = fields.Nested('InventorySchema', exclude=('id',))
    service = fields.Nested('ServiceSchema', exclude=('id', 'service_items',))
    mechanic_tickets = fields.Nested('MechanicTicketSchema', exclude=('additional_items'))

    @validates('quantity')
    def validate_quantity(self, value):
        if not value:
            raise ValidationError("Quantity is required.")
        

service_item_schema = ServiceItemSchema()
service_items_schema = ServiceItemSchema(many=True)