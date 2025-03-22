
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select
from datetime import date
from . import invoices_bp
from app.models import Invoice, db, ServiceTicket
from app.extensions import limiter, cache
from .schemas import invoice_schema, invoices_schema
from app.utils.util import token_required, mechanic_token_required


# Create Invoice
@invoices_bp.route('/', methods=['POST'])
@mechanic_token_required
def create_invoice():
    try:
        invoice_data = invoice_schema.load(request.json)
    except ValidationError as ve:
        return jsonify(ve.messages), 400
    
    service_ticket = db.session.get(ServiceTicket, invoice_data['service_ticket_id'])
    if not service_ticket:
        return jsonify({"message": "Invalid Service Ticket ID"}), 404
    
    invoice = Invoice(
        invoice_date=invoice_data.get('invoice_date') or date.today(),
        paid=invoice_data.get('paid') or False,
        service_ticket_id=service_ticket.id
    )

    db.session.add(invoice)
    db.session.commit()
    return jsonify(invoice_schema.dump(invoice)), 201


# Read/Get All Invoices
@invoices_bp.route('/', methods=['GET'])
@limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve all Invoices more than 10 per hour
@cache.cached(timeout=60)
# Cache the response for 60 seconds
# This will help reduce the load on the database
@mechanic_token_required
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
@limiter.limit("10 per hour")
# Limit the number of retrievals to 10 per hour
# There shouldn't be a need to retrieve a single Invoice more than 10 per hour
@mechanic_token_required
# Only mechanics can retrieve a single Invoice
def get_invoice(id):
    invoice = db.session.get(Invoice, id)

    if not invoice:
        return jsonify({"message": "Invalid Invoice ID"}), 404

    return jsonify(invoice_schema.dump(invoice)), 200


# Update Invoice
@invoices_bp.route('/<int:id>', methods=['PUT'])
@mechanic_token_required
def update_invoice(id):
    invoice = db.session.get(Invoice, id)

    if not invoice:
        return jsonify({"message": "Invalid Invoice ID"}), 404
    
    try:
        invoice_data = invoice_schema.load(request.json, partial=True)
    except ValidationError as ve:
        return jsonify(ve.messages), 400
    
    invoice.paid = invoice_data.get('paid') or False
    invoice.service_ticket_id = invoice_data.get('service_ticket_id') or invoice.service_ticket_id

    db.session.commit()
    return jsonify(invoice_schema.dump(invoice)), 200


# Delete Invoice