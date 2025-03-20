
from app.extensions import ma
from app.models import Invoice
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class InvoiceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Invoice
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    invoice_date = fields.Date(required=False, dump_only=True)
    total = fields.Method('calculate_total')
    paid = fields.Boolean(required=True)
    service_ticket_id = fields.Int(required=True, validate=Length(min=1))

    service_ticket = fields.Nested('ServiceTicketSchema', exclude=('invoice', 'id',))

    def calculate_total(self, obj):
        total = 0.0

        if obj.service_ticket:
            for mt in obj.service_ticket.mechanic_tickets:
                mt_cost = 0.0

                if mt.services:
                    for s in mt.services:
                        s_cost = s.price
                        for i in s.service_items:
                            s_cost = i.quantity * i.inventory.price
                        mt_cost += s_cost
                            
                if mt.additional_items:
                    for ai in mt.additional_items:
                        mt_cost += ai.quantity * ai.inventory.price

                total += mt_cost

        return round(total, 2)


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