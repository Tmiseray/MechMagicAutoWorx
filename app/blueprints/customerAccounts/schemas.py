
from app.extensions import ma
from app.models import CustomerAccount
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class CustomerAccountSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CustomerAccount
        include_relationships = True
        load_instance = True

    id = fields.Int(dump_only=True)
    email = fields.Str(required=True, validate=Email())
    password = fields.Str(required=True, validate=Length(min=8, max=100), load_only=True)

    customer = fields.Nested('CustomerSchema', exclude=('account',))

    @validates('email')
    def validate_email(self, value):
        if not value:
            raise ValidationError("Email is required.")
        

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)