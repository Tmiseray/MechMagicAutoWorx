
from app.extensions import ma
from app.models import ServiceTicket, db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class ServiceTicketSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        include_relationships = True
        load_instance = True
        sqla_session = db.session

    id = fields.Int(dump_only=True)
    service_date = fields.Date(required=True)
    service_desc = fields.Str(required=True, validate=Length(min=1, max=255))
    VIN = fields.Str(required=True)
    customer_id = fields.Int(required=False)

    vehicle = fields.Nested('VehicleSchema', exclude=('VIN', 'service_tickets', 'customer', 'customer_id',))
    customer = fields.Nested('CustomerSchema', exclude=('service_tickets', 'id', 'account', 'vehicles',))
    mechanic_tickets = fields.List(fields.Nested('MechanicTicketSchema', exclude=('service_ticket',)), default=[])
    invoice = fields.Nested('InvoiceSchema', exclude=('service_ticket', 'service_ticket_id',))

    @validates('service_date')
    def validate_service_date(self, value):
        if not value:
            raise ValidationError("Service Date (service_date) is required.")

    @validates('service_desc')
    def validate_service_desc(self, value):
        if not value:
            raise ValidationError("Service Description (service_desc) is required.")
        
    @validates('VIN')
    def validate_VIN(self, value):
        if not value:
            raise ValidationError("VIN is required.")


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
    