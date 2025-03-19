
from app.extensions import ma
from app.models import Customer
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class CustomerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(min=1, max=100))
    email = fields.Str(required=True, validate=Email())
    phone = fields.Str(required=True, validate=Length(min=1, max=100))

    vehicles = fields.List(fields.Nested('VehicleSchema', many=True, exclude=('customer',)))
    account = fields.Nested('CustomerAccountSchema', exclude=('customer',))
    service_tickets = fields.List(fields.Nested('ServiceTicketSchema', many=True, exclude=('customer',)))

    @validates('email')
    def validate_email(self, value):
        if not value:
            raise ValidationError("Email is required.")
        if '@' not in value:
            raise ValidationError("Invalid email address.")


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)