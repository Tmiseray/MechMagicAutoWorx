
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from . import customer_accounts_bp
from app.models import CustomerAccount, db, Customer
from app.extensions import limiter, cache
from .schemas import customer_account_schema, customer_accounts_schema
from app.utils.util import token_required, mechanic_token_required, encode_token


# Customer Login
@customer_accounts_bp.route('/login', methods=['POST'])
def login():
    try:
        credentials = customer_account_schema.load(request.json, partial=True)
        email = credentials['email']
        password = credentials['password']
    except KeyError:
        return jsonify({"message": "Expecting Email and Password"}), 400
    
    query = select(CustomerAccount).where(CustomerAccount.email==email)
    account = db.session.execute(query).scalar_one_or_none()

    if account and account.check_password(password):
        auth_token = encode_token(account.customer_id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({"message": "Invalid Credentials"}), 401


# Create CustomerAccount
@customer_accounts_bp.route('/', methods=['POST'])
def create_customer_account():
    try:
        account_data = customer_account_schema.load(request.json)
    except ValidationError as ve:
        return jsonify(ve.messages), 404
    
    customer = db.session.get(Customer, account_data['customer_id'])

    if not customer:
        return jsonify({"message": f"Invalid Customer ID: {account_data['customer_id']}"}), 404
    
    account = CustomerAccount(
        customer_id=customer.id,
        email=account_data['email']
    )
    account.password = account.set_password(account_data['password'])
    db.session.add(account)
    db.session.commit()
    return jsonify(customer_account_schema.dump(account))

# Read/Get All CustomerAccounts
@customer_accounts_bp.route('/all', methods=['GET'])
@limiter.limit("3 per hour")
# Limit the number of retrievals to 3 per hour
# There shouldn't be a need to retrieve all Customers' Accounts more than 3 per hour
@cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
@mechanic_token_required
# Only mechanics can retrieve all Customers' Accounts
def get_customer_accounts():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(CustomerAccount)
        result = db.paginate(query, page=page, per_page=per_page)
        return jsonify(customer_accounts_schema.dump(result)), 200
    except:
        query = select(CustomerAccount)
        result = db.session.execute(query).scalars().all()
        return jsonify(customer_accounts_schema.dump(result)), 200

# Read/Get Specific CustomerAccount
@customer_accounts_bp.route('/', methods=['GET'])
@limiter.limit("3 per hour")
# Limit the number of retrievals to 3 per hour
# There shouldn't be a need to retrieve a single customer account more than 3 per hour
@token_required
# Only that customer can retrieve their account details
def get_customer_account(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Customer or Account not found"}), 404

    account = db.session.get(CustomerAccount, customer.account.id)
    return jsonify(customer_account_schema.dump(account)), 200


# Update CustomerAccount
@customer_accounts_bp.route('/', methods=['PUT'])
@limiter.limit("2 per day")
# Limit the number of updates to 2 per day
# There shouldn't be a need to update the customer account more than 2 per day
@token_required
# Only that customer can update their account
def update_customer_account(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Customer or Account not found"}), 404
    
    try:
        account_data = customer_account_schema.load(request.json, partial=True)
    except ValidationError as ve:
        return jsonify(ve.messages), 400
    
    account = db.session.get(CustomerAccount, customer.account.id)
    
    account.email = account_data.get('email') or account.email
    account.password = account.set_password(account_data['password']) or account.password

    db.session.commit()

    return jsonify(customer_account_schema.dump(account)), 200


# Delete CustomerAccount
@customer_accounts_bp.route('/', methods=['DELETE'])
@token_required
def delete_customer_account(id):
    customer = db.session.get(Customer, id)
    account = db.session.get(CustomerAccount, customer.account.id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "Account Successfully Deleted"}), 200