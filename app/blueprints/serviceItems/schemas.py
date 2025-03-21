
from app.extensions import ma
from app.models import ServiceItem
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError


class ServiceItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceItem
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    item_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    service_id = fields.Int(required=False)

    inventory = fields.Nested('InventorySchema', exclude=('id',))
    service = fields.Nested('ServiceSchema', exclude=('id', 'service_items',))
    mechanic_tickets = fields.Nested('MechanicTicketSchema', exclude=('additional_items'))

    @validates('quantity')
    def validate_quantity(self, value):
        if not value:
            raise ValidationError("Quantity is required.")
        if value < 1:
            raise ValidationError("Quantity must be at least 1.")
        

service_item_schema = ServiceItemSchema()
service_items_schema = ServiceItemSchema(many=True)