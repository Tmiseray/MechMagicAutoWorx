from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import date


# Create a base class for our models
class Base(DeclarativeBase):
    pass

# Instantiate your SQLAlchemy database
db = SQLAlchemy(model_class = Base)


# Customer Model
class Customer(Base):
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(100), nullable=False)

    vehicles: Mapped[Optional[List['Vehicle']]] = db.relationship('Vehicle', back_populates='customer')

    account: Mapped['CustomerAccount'] = db.relationship('CustomerAccount', back_populates='customer', uselist=False)

    service_tickets: Mapped[Optional[List['ServiceTicket']]] = db.relationship('ServiceTicket', back_populates='customer')


# CustomerAccount Model
class CustomerAccount(Base):
    __tablename__ = 'customer_accounts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String, db.ForeignKey('customers.email'), nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)

    customer: Mapped['Customer'] = db.relationship('Customer', back_populates='account', uselist=False)


# Invoice Model
class Invoice(Base):
    __tablename__ = 'invoices'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_date: Mapped[date] = mapped_column(db.Date, nullable=False, default=date.today())
    total: Mapped[float] = mapped_column(db.Float, nullable=False)
    paid: Mapped[bool] = mapped_column(db.Boolean, nullable=False)

    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.id'))
    service_ticket: Mapped['ServiceTicket'] = db.relationship('ServiceTicket', back_populates='invoice')


# Vehicle Model
class Vehicle(Base):
    __tablename__ = 'vehicles'
    
    VIN: Mapped[str] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(db.Integer, nullable=False)
    make: Mapped[str] = mapped_column(db.String(100), nullable=False)
    model: Mapped[str] = mapped_column(db.String(100), nullable=False)
    mileage: Mapped[int] = mapped_column(db.Integer, nullable=False)

    customer: Mapped['Customer'] = db.relationship('Customer', back_populates='vehicles')


# Mechanic Model
class Mechanic(Base):
    __tablename__ = 'mechanics'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(100), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    account: Mapped['MechanicAccount'] = db.relationship('MechanicAccount', back_populates='mechanic', uselist=False)

    mechanic_tickets: Mapped[List['MechanicTicket']] = db.relationship('MechanicTicket', back_populates='mechanic')


# MechanicAccount Model
class MechanicAccount(Base):
    __tablename__ = 'customer_accounts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(db.String(100), nullable=False, default="Mechanic")
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)

    email: Mapped[str] = mapped_column(db.String, db.ForeignKey('mechanics.email'), nullable=False)
    mechanic: Mapped['Mechanic'] = db.relationship('Mechanic', back_populates='account', uselist=False)


# MechanicTicket Model
class MechanicTicket(Base):  
    __tablename__ = 'mechanic_tickets'  

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(db.Date, nullable=True)
    hours_worked: Mapped[Optional[List[float]]] = mapped_column(db.Float, nullable=False)

    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.id'))
    service_ticket: Mapped['ServiceTicket'] = db.relationship('ServiceTicket', back_populates='mechanic_tickets')

    mechanic_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey('mechanics.id', ondelete='SET NULL'), nullable=True)
    mechanic: Mapped['Mechanic'] = db.relationship('Mechanic', back_populates='mechanic_tickets')

    service_id: Mapped[int] = mapped_column(db.ForeignKey('services.id', ondelete='SET NULL'), nullable=False)
    services: Mapped[List['Service']] = db.relationship('Service', back_populates='mechanic_tickets')

    additional_item_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey('service_items.item_id', ondelete='SET NULL'), nullable=True)
    additional_items: Mapped[Optional[List['ServiceItem']]] = db.relationship('ServiceItem', back_populates='mechanic_ticket')


# Inventory Model
class Inventory(Base):
    __tablename__ = 'inventory'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    stock: Mapped[int] = mapped_column(db.Integer, nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

# ServiceItem Model
class ServiceItem(Base):
    __tablename__ = 'service_items'
    item_id: Mapped[int] = mapped_column(db.ForeignKey('inventory.id'), primary_key=True)
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)

    service: Mapped['Service'] = db.relationship('Service', back_populates='service_items')

    mechanic_ticket: Mapped[Optional['MechanicTicket']] = db.relationship('MechanicTicket', back_populates='additional_items')

# Service Model
class Service(Base):
    __tablename__ = 'services'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_item_id: Mapped[int] = mapped_column(db.ForeignKey('service_items.item_id'))
    service_items: Mapped[List['ServiceItem']] = db.relationship('ServiceItem', back_populates='service')

    mechanic_tickets: Mapped[Optional[List['MechanicTicket']]] = db.relationship('MechanicTicket', back_populates='services')


# ServiceTicket Model
class ServiceTicket(Base):
    __tablename__ = 'service_tickets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String, db.ForeignKey('vehicles.VIN'), nullable=False)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(255), nullable=False)

    customer_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True)
    customer: Mapped['Customer'] = db.relationship('Customer', back_populates='service_tickets')

    mechanic_tickets: Mapped[Optional[List['MechanicTicket']]] = db.relationship('MechanicTicket', back_populates='service_ticket')

    invoice: Mapped['Invoice'] = db.relationship('Invoice', back_populates='service_ticket')



