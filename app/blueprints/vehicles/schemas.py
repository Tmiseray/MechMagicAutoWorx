
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

    VIN = fields.Str(required=True, validate=Length(min=17, max=100))
    year = fields.Int(required=True)
    make = fields.Str(required=True, validate=Length(min=1, max=100))
    model = fields.Str(required=True, validate=Length(min=1, max=100))
    customer_id = fields.Int(required=True)
    
    customer = fields.Nested('CustomerSchema', exclude=('vehicles', 'id',))
    service_tickets = fields.Nested('ServiceTicketSchema', many=True, exclude=('vehicle',))

    @validates('VIN')
    def validate_vin(self, value):
        if not value:
            raise ValidationError("VIN is required.")
        
    @validates('year')
    def validate_year(self, value):
        if not value:
            raise ValidationError("Year is required.")
        
    @validates('make')
    def validate_make(self, value):
        if not value:
            raise ValidationError("Make is required.")
        
    @validates('model')
    def validate_model(self, value):
        if not value:
            raise ValidationError("Model is required.")
        
    @validates('customer_id')
    def validate_customer_id(self, value):
        if not value:
            raise ValidationError("Customer ID is required.")
        

vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)