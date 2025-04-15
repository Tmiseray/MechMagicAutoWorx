
from app.models import MechanicTicket, db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError


class MechanicTicketSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MechanicTicket
        include_relationships = True
        load_instance = True
        sqla_session = db.session

    id = fields.Int(dump_only=True)
    start_date = fields.Date(required=False, dump_only=True)
    end_date = fields.Date(required=False)
    hours_worked = fields.Float(required=False)
    service_ticket_id = fields.Int(required=True)
    mechanic_id = fields.Int(required=False)

    service_ticket = fields.Nested('ServiceTicketSchema', exclude=('mechanic_tickets', 'id',))
    mechanic = fields.Nested('MechanicSchema', only=('name',))
    services = fields.List(fields.Nested('ServiceSchema', exclude=('mechanic_tickets', )), default=[])
    additional_items = fields.List(fields.Nested('ServiceItemSchema', exclude=('mechanic_tickets', 'service_id', 'service',)), default=[])

    @validates('service_ticket_id')
    def validate_service_ticket_id(self, value):
        if not value:
            raise ValidationError("Service Ticket ID (service_ticket_id) is required.")
        

mechanic_ticket_schema = MechanicTicketSchema()
mechanic_tickets_schema = MechanicTicketSchema(many=True)