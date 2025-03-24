
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from datetime import date
from . import invoices_bp
from app.models import Invoice, db, ServiceTicket
from app.extensions import limiter, cache
from .schemas import invoice_schema, invoices_schema
from app.utils.util import token_required, mechanic_token_required
from app.utils.validation_creation import validate_and_create, validate_foreign_key, validate_and_update


# Create Invoice
@invoices_bp.route('/', methods=['POST'])
# @mechanic_token_required
def create_invoice():
    payload = request.json

    try:
        validate_foreign_key(ServiceTicket, payload.get('service_ticket_id'), "Service Ticket ID")
    except ValueError as e:
        return jsonify({"message": str(e)}), 404

    new_invoice, err = validate_and_create(Invoice, invoice_schema, payload)
    if err:
        return err

    return jsonify(invoice_schema.dump(new_invoice)), 201


# Read/Get All Invoices
@invoices_bp.route('/all', methods=['GET'])
# @limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve all Invoices more than 10 per hour
# @cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
# @mechanic_token_required
# Only mechanics can retrieve all Invoices
def get_invoices():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        query = select(Invoice)
        result = db.paginate(query, page=page, per_page=per_page)
        return jsonify(invoices_schema.dump(result)), 200
    except:
        query = select(Invoice)
        result = db.session.execute(query).scalars().all()
        return jsonify(invoices_schema.dump(result)), 200


# Read/Get Specific Invoice
@invoices_bp.route('/<int:id>', methods=['GET'])
# @limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve a single Invoice more than 10 per hour
# @mechanic_token_required
# Only mechanics can retrieve a single Invoice
def get_invoice(id):
    invoice = db.session.get(Invoice, id)

    if not invoice:
        return jsonify({"message": "Invalid Invoice ID"}), 404

    return jsonify(invoice_schema.dump(invoice)), 200


# Get customer's invoices
@invoices_bp.route('/my-invoices/<int:customer_id>', methods=['GET'])
# @limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve a customer's invoices more than 10 per hour
# @token_required
def get_my_invoices(customer_id):
    query = select(Invoice).where(Invoice.service_ticket.customer_id == customer_id)
    invoices = db.session.execute(query).scalars().all()

    return jsonify(invoices_schema.dump(invoices)), 200


# Update Invoice
@invoices_bp.route('/<int:id>', methods=['PUT'])
# @mechanic_token_required
def update_invoice(id):
    invoice = db.session.get(Invoice, id)
    if not invoice:
        return jsonify({"message": "Invalid Invoice ID"}), 404

    payload = request.json

    # Validate foreign keys (if changing service_ticket_id)
    fk_result = validate_foreign_key(payload, {
        "service_ticket_id": ServiceTicket
    })
    if fk_result:
        return fk_result

    # Update invoice fields safely
    success, response, status_code = validate_and_update(
        instance=invoice,
        schema=invoice_schema,
        payload=payload,
        foreign_keys={}  # already validated
    )
    return response, status_code


# Delete Invoice
'''
Preserving Invoice history due to it being crucial for recording-keeping, taxes, audits, and warranty disputes
'''