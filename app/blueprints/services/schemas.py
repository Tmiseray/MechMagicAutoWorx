
from app.extensions import ma
from app.models import Service
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length


class ServiceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Service
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(min=1, max=100))
    price = fields.Float(required=True)

    service_items = fields.List(fields.Nested('ServiceItemSchema', exclude=('service',)))
    mechanic_tickets = fields.List(fields.Nested('MechanicTicketSchema', exclude=('services',)))

    @validates('name')
    def validate_name(self, value):
        if not value:
            raise ValidationError("Name is required.")
    
    @validates('price')
    def validate_price(self, value):
        if not value:
            raise ValidationError("Price is required.")
        

service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)
