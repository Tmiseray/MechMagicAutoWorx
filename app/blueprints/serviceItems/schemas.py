
from app.models import ServiceItem, db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError


class ServiceItemSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceItem
        include_relationships = True
        load_instance = True
        sqla_session = db.session

    id = fields.Int(dump_only=True)
    item_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    service_id = fields.Int(required=False, allow_none=True)

    inventory = fields.Nested('InventorySchema', only=('name', 'stock', 'price',))
    service = fields.Nested('ServiceSchema', only=('name', 'price',))
    mechanic_tickets = fields.List(fields.Nested('MechanicTicketSchema', only=('id', 'start_date', 'end_date', 'mechanic_id',)))

    @validates('quantity')
    def validate_quantity(self, value):
        if not value:
            raise ValidationError("Quantity is required.")
        if value < 1:
            raise ValidationError("Quantity must be at least 1.")
        

service_item_schema = ServiceItemSchema()
service_items_schema = ServiceItemSchema(many=True)