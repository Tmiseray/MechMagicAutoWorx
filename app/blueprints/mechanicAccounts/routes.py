
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanic_accounts_bp
from app.models import MechanicAccount, db, Mechanic
from app.extensions import limiter, cache
from .schemas import mechanic_account_schema, mechanic_accounts_schema, mechanic_login_schema
from app.utils.util import mechanic_token_required, encode_mechanic_token, check_password
from app.utils.validation_creation import validate_and_create, validate_and_update


# Mechanic Login
@mechanic_accounts_bp.route('/login', methods=['POST'])
def login():
    try:
        credentials = mechanic_login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except KeyError:
        return jsonify({"message": "Expecting Email and Password"}), 400
    
    query = select(MechanicAccount).where(MechanicAccount.email==email)
    account = db.session.execute(query).scalar_one_or_none()
    print("Password match:", check_password(password, account.password))
    print("DB password:", account.password)
    print("Customer password:", password)
    print("Type:", type(account.password))

    if account and check_password(password, account.password):
        auth_token = encode_mechanic_token(account.mechanic_id, account.role)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({"message": "Invalid Credentials"}), 401


# Create MechanicAccount
@mechanic_accounts_bp.route('/', methods=['POST'])
def create_mechanic_account():
    payload = request.json

    return validate_and_create(
        model=MechanicAccount,
        payload=payload,
        schema=mechanic_account_schema,
        unique_fields=['email'],
        case_insensitive_fields=['email'],
        foreign_keys={
            "mechanic_id": Mechanic
        },
        commit=True,
        return_json=True
    )

# Read/Get All MechanicAccounts
@mechanic_accounts_bp.route('/all', methods=['GET'])
# @limiter.limit("3 per hour")
# # Limit the number of retrievals to 3 per hour
# # There shouldn't be a need to retrieve all Mechanics' Accounts more than 3 per hour
# @cache.cached(timeout=60)
# # Cache the response for 60 seconds
# # This will help reduce the load on the database
# @mechanic_token_required
# Only mechanics can retrieve all mechanics' Accounts
def get_mechanic_accounts():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(MechanicAccount)
        result = db.paginate(query, page=page, per_page=per_page)
        return jsonify(mechanic_accounts_schema.dump(result)), 200
    except:
        query = select(MechanicAccount)
        result = db.session.execute(query).scalars().all()
        return jsonify(mechanic_accounts_schema.dump(result)), 200

# Read/Get Specific MechanicAccount
@mechanic_accounts_bp.route('/<int:id>', methods=['GET'])
# @mechanic_accounts_bp.route('/', methods=['GET'])
# @limiter.limit("3 per hour")
# # Limit the number of retrievals to 3 per hour
# # There shouldn't be a need to retrieve a single mechanic account more than 3 per hour
# @mechanic_token_required
# # Only that mechanic can retrieve their account details
def get_mechanic_account(id):
    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"message": "Mechanic or Account not found"}), 404

    account = db.session.get(MechanicAccount, mechanic.account.id)
    return jsonify(mechanic_account_schema.dump(account)), 200

# Update MechanicAccount
@mechanic_accounts_bp.route('/<int:id>', methods=['PUT'])
# @mechanic_accounts_bp.route('/', methods=['PUT'])
# @limiter.limit("2 per day")
# # Limit the number of updates to 2 per day
# # There shouldn't be a need to update the mechanic account more than 2 per day
# @mechanic_token_required
# Only that mechanic can update their account
def update_mechanic_account(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic or not mechanic.account:
        return jsonify({"message": "Mechanic or Account not found"}), 404

    payload = request.json
    account = mechanic.account

    # If password is being updated, use the model's method
    if 'password' in payload:
        account.set_password(payload['password'])
        del payload['password']  # Prevent overwriting hashed password

    # Validate and update remaining fields
    success, response, status_code = validate_and_update(
        instance=account,
        schema=mechanic_account_schema,
        payload=payload,
        foreign_keys={},
        return_json=True
    )
    return response, status_code

# Delete MechanicAccount
@mechanic_accounts_bp.route('/<int:id>', methods=['DELETE'])
# @mechanic_accounts_bp.route('/', methods=['DELETE'])
# @mechanic_token_required
def delete_mechanic_account(id):
    mechanic = db.session.get(Mechanic, id)
    account = db.session.get(MechanicAccount, mechanic.account.id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "Account Successfully Deleted"}), 200