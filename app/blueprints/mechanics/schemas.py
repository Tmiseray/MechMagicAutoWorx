
from app.models import Mechanic, db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class MechanicSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        include_relationships = True
        load_instance = True
        sqla_session = db.session

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=Length(min=1, max=100))
    email = fields.Str(required=True, validate=Email())
    phone = fields.Str(required=True, validate=Length(min=10, max=100))
    salary = fields.Float(required=True)

    account = fields.Nested('MechanicAccountSchema', exclude=('mechanic', 'mechanic_id', 'email', 'id', ))
    mechanic_tickets = fields.List(fields.Nested('MechanicTicketSchema', exclude=('mechanic', 'mechanic_id',)), default=[])

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
        
    @validates('salary')
    def validate_salary(self, value):
        if not value:
            raise ValidationError("Salary is required.")
        

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)