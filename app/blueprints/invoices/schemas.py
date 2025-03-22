
from app.extensions import ma
from app.models import Invoice
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError


class InvoiceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Invoice
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    invoice_date = fields.Date(required=False, dump_only=True)
    total = fields.Method('get_total')
    paid = fields.Boolean(required=True)
    service_ticket_id = fields.Int(required=True)

    service_ticket = fields.Nested('ServiceTicketSchema', exclude=('invoice', 'id',))

    def get_total(self, obj):
        return obj.calculate_total()


    @validates('paid')
    def validate_paid(self, value):
        if value not in [True, False]:
            raise ValidationError("Paid is required to be 'True' or 'False'.")
        
    @validates('service_ticket_id')
    def validate_service_ticket_id(self, value):
        if not value:
            raise ValidationError("Service Ticket ID (service_ticket_id) is required.")
        

invoice_schema = InvoiceSchema()
invoices_schema = InvoiceSchema(many=True)