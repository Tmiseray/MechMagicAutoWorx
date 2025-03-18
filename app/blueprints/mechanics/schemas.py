
from app.extensions import ma
from app.models import Mechanic
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class MechanicSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(min=1, max=100))
    email = fields.Str(required=True, validate=Email())
    phone = fields.Str(required=True, validate=Length(min=1, max=100))
    salary = fields.Float(required=True)

    account = fields.Nested('MechanicAccountSchema', exclude=('mechanic',))
    mechanic_tickets = fields.Nested('MechanicTicketSchema', many=True, exclude=('mechanic',))

    @validates('email')
    def validate_email(self, value):
        if not value:
            raise ValidationError("Email is required.")
        if '@' not in value:
            raise ValidationError("Invalid email address.")
        

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)