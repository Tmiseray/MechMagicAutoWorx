
from app.extensions import ma
from app.models import Customer, db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class CustomerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        include_relationships = True
        load_instance = True
        sqla_session = db.session

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(min=1, max=100))
    email = fields.Str(required=True, validate=Email())
    phone = fields.Str(required=True, validate=Length(min=10, max=100))

    vehicles = fields.List(fields.Nested('VehicleSchema', many=True, exclude=('customer',)), default=[])
    account = fields.Nested('CustomerAccountSchema', exclude=('customer',))
    service_tickets = fields.List(fields.Nested('ServiceTicketSchema', many=True, exclude=('customer',)), default=[])

    @validates('name')
    def validate_name(self, value):
        if not value:
            raise ValidationError("Name is required.")
        
    @validates('email')
    def validate_email(self, value):
        if not value:
            raise ValidationError("Email is required.")

    @validates('phone')
    def validate_phone(self, value):
        if not value:
            raise ValidationError("Phone is required.")


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)