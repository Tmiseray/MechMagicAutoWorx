from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import date
from .utils.util import hash_password, check_password


# Create a base class for our models
class Base(DeclarativeBase):
    pass

# Instantiate your SQLAlchemy database
db = SQLAlchemy(model_class = Base)


# ------------------------------------------------
# Association Tables
# ------------------------------------------------

# Association Table for Services & MechanicTickets
mechanic_ticket_services = db.Table(
    'mechanic_ticket_services',
    db.Column('mechanic_ticket_id', db.ForeignKey('mechanic_tickets.id'), primary_key=True),
    db.Column('service_id', db.ForeignKey('services.id'), primary_key=True)
)

# Association Table for ServiceItems & MechanicTickets
mechanic_ticket_items = db.Table(
    'mechanic_ticket_items',
    db.Column('mechanic_ticket_id', db.ForeignKey('mechanic_tickets.id'), primary_key=True),
    db.Column('service_item_id', db.ForeignKey('service_items.id'), primary_key=True)
)

# ------------------------------------------------
# Model Tables
# ------------------------------------------------

# Customer Model
class Customer(Base):
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)

    vehicles: Mapped[Optional[List['Vehicle']]] = db.relationship('Vehicle', back_populates='customer')

    account: Mapped[Optional['CustomerAccount']] = db.relationship('CustomerAccount', back_populates='customer', uselist=False)

    service_tickets: Mapped[Optional[List['ServiceTicket']]] = db.relationship('ServiceTicket', back_populates='customer')


# CustomerAccount Model
class CustomerAccount(Base):
    __tablename__ = 'customer_accounts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    customer: Mapped['Customer'] = db.relationship('Customer', back_populates='account', uselist=False)

    def __init__(self, email, password, **kwargs):
        super().__init__(email=email, **kwargs)
        self.set_password(password)

    def set_password(self, raw_password):
        self.password = hash_password(raw_password)

    def validate_password(self, raw_password):
        return check_password(raw_password, self.password)
    

# Invoice Model
class Invoice(Base):
    __tablename__ = 'invoices'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    total: Mapped[float] = mapped_column(db.Float, nullable=False)
    paid: Mapped[bool] = mapped_column(db.Boolean, nullable=False)

    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.id'))
    service_ticket: Mapped['ServiceTicket'] = db.relationship('ServiceTicket', back_populates='invoice')

    def calculate_total(self):
        total = 0.0

        if self.service_ticket:
            for mt in self.service_ticket.mechanic_tickets:
                mt_cost = 0.0

                if mt.services:
                    for s in mt.services:
                        s_cost = s.price
                        for i in s.service_items:
                            s_cost += i.quantity * i.inventory.price
                        mt_cost += s_cost
                            
                if mt.additional_items:
                    for ai in mt.additional_items:
                        mt_cost += ai.quantity * ai.inventory.price

                total += mt_cost

        return round(total, 2)


# Vehicle Model
class Vehicle(Base):
    __tablename__ = 'vehicles'
    
    VIN: Mapped[str] = mapped_column(db.String(100), primary_key=True)
    year: Mapped[int] = mapped_column(db.Integer, nullable=False)
    make: Mapped[str] = mapped_column(db.String(100), nullable=False)
    model: Mapped[str] = mapped_column(db.String(100), nullable=False)
    mileage: Mapped[int] = mapped_column(db.Integer, nullable=False)

    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True)
    customer: Mapped['Customer'] = db.relationship('Customer', back_populates='vehicles')

    service_tickets: Mapped[Optional[List['ServiceTicket']]] = db.relationship('ServiceTicket', back_populates='vehicle')


# Mechanic Model
class Mechanic(Base):
    __tablename__ = 'mechanics'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    account: Mapped[Optional['MechanicAccount']] = db.relationship('MechanicAccount', back_populates='mechanic', uselist=False)

    mechanic_tickets: Mapped[List['MechanicTicket']] = db.relationship('MechanicTicket', back_populates='mechanic')


# MechanicAccount Model
class MechanicAccount(Base):
    __tablename__ = 'mechanic_accounts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(db.String(10), nullable=False, default="Mechanic")
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    mechanic_id: Mapped[int] = mapped_column(db.ForeignKey('mechanics.id', ondelete='SET NULL'), nullable=True)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False)
    mechanic: Mapped['Mechanic'] = db.relationship('Mechanic', back_populates='account', uselist=False)

    def __init__(self, email, password, **kwargs):
        super().__init__(email=email, **kwargs)
        self.set_password(password)

    def set_password(self, raw_password):
        self.password = hash_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


# MechanicTicket Model
class MechanicTicket(Base):  
    __tablename__ = 'mechanic_tickets'  

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(db.Date, nullable=True)
    hours_worked: Mapped[Optional[float]] = mapped_column(db.Float, nullable=False)

    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.id'))
    service_ticket: Mapped['ServiceTicket'] = db.relationship('ServiceTicket', back_populates='mechanic_tickets')

    mechanic_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey('mechanics.id', ondelete='SET NULL'), nullable=True)
    mechanic: Mapped['Mechanic'] = db.relationship('Mechanic', back_populates='mechanic_tickets')

    services: Mapped[Optional[List['Service']]] = db.relationship('Service', secondary=mechanic_ticket_services, back_populates='mechanic_tickets')

    additional_items: Mapped[Optional[List['ServiceItem']]] = db.relationship('ServiceItem', secondary=mechanic_ticket_items, back_populates='mechanic_tickets')


# Inventory Model
class Inventory(Base):
    __tablename__ = 'inventory'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    stock: Mapped[int] = mapped_column(db.Integer, nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_items: Mapped[List['ServiceItem']] = db.relationship('ServiceItem', back_populates='inventory')

# ServiceItem Model
class ServiceItem(Base):
    __tablename__ = 'service_items'
    id: Mapped[int] = mapped_column(primary_key=True)

    item_id: Mapped[int] = mapped_column(db.ForeignKey('inventory.id'), nullable=False)
    inventory: Mapped['Inventory'] = db.relationship('Inventory', back_populates='service_items')
    
    service_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey('services.id', ondelete='SET NULL'), nullable=True)
    service: Mapped[Optional['Service']] = db.relationship('Service', back_populates='service_items')
    
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)

    mechanic_tickets = db.relationship('MechanicTicket', secondary=mechanic_ticket_items, back_populates='additional_items')

# Service Model
class Service(Base):
    __tablename__ = 'services'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_items: Mapped[List['ServiceItem']] = db.relationship('ServiceItem', back_populates='service')

    mechanic_tickets = db.relationship('MechanicTicket', secondary=mechanic_ticket_services, back_populates='services')


# ServiceTicket Model
class ServiceTicket(Base):
    __tablename__ = 'service_tickets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False, default=date.today())
    service_desc: Mapped[str] = mapped_column(db.String(255), nullable=False)

    VIN: Mapped[str] = mapped_column(db.String(100), db.ForeignKey('vehicles.VIN'), nullable=False)
    vehicle: Mapped['Vehicle'] = db.relationship('Vehicle', back_populates='service_tickets')

    customer_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True)
    customer: Mapped['Customer'] = db.relationship('Customer', back_populates='service_tickets')

    mechanic_tickets: Mapped[Optional[List['MechanicTicket']]] = db.relationship('MechanicTicket', back_populates='service_ticket')

    invoice: Mapped['Invoice'] = db.relationship('Invoice', back_populates='service_ticket')



