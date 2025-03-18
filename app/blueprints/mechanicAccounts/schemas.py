
from app.extensions import ma
from app.models import MechanicAccount
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class MechanicAccountSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MechanicAccount
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    email = fields.Str(required=True, validate=Email())
    password = fields.Str(required=True, validate=Length(min=1, max=100))

    @validates('email')
    def validate_email(self, value):
        if not value:
            raise ValidationError("Email is required.")
        if '@' not in value:
            raise ValidationError("Invalid email address.")


mechanic_account_schema = MechanicAccountSchema()
mechanic_accounts_schema = MechanicAccountSchema(many=True)
