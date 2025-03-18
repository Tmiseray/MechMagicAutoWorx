
from app.extensions import ma
from app.models import Vehicle
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class VehicleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        include_relationships = True
        load_instance = True

    VIN = fields.Str(required=True, validate=Length(min=1, max=100))
    year = fields.Int(required=True)
    make = fields.Str(required=True, validate=Length(min=1, max=100))
    model = fields.Str(required=True, validate=Length(min=1, max=100))
    # customer_id = fields.Int(required=True)
    
    customer = fields.Nested('CustomerSchema', exclude=('vehicles',))
    service_tickets = fields.Nested('ServiceTicketSchema', many=True, exclude=('vehicle',))

    @validates('VIN')
    def validate_vin(self, value):
        if not value:
            raise ValidationError("VIN is required.")
        if len(value) != 17:
            raise ValidationError("VIN must be 17 characters long.")
        

vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)