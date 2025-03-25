
from app.extensions import ma
from app.models import MechanicAccount, db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Length, Email


class MechanicAccountSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MechanicAccount
        include_relationships = True
        load_instance = True
        sqla_session = db.session

    id = fields.Int(dump_only=True)
    role = fields.Str(dump_only=True)
    mechanic_id = fields.Int(required=True)
    email = fields.Str(required=True, validate=Email())
    password = fields.Str(required=True, validate=Length(min=8, max=100))

    # , load_only=True Add to above

    mechanic = fields.Nested('MechanicSchema', exclude=('account', 'id', 'email',))

    @validates('email')
    def validate_email(self, value):
        if not value:
            raise ValidationError("Email is required.")
        
    @validates('password')
    def validate_password(self, value):
        if not value:
            raise ValidationError("Password is required.")
        

class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=Length(min=8))


mechanic_account_schema = MechanicAccountSchema()
mechanic_accounts_schema = MechanicAccountSchema(many=True)
mechanic_login_schema = LoginSchema()