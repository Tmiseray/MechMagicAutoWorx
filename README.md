# MechMagicAutoWorx
 Coding Temple - Python Back-End Project

This project is a Flask-based web application designed to manage mechanics, customers, and service tickets. 
It utilizes Flask Blueprints for modularization and Marshmallow for object serialization and deserialization.
Limiter, Caching, Specific Token Requirements (Customer Token is ***DIFFERENT*** than Mechanic Token), and Hashing of passwords have all been implemented. As well as, reusable functions within `app.utils.validation_creation` for validations, creations, and updates.

***NOTE:*** A Testing Config has not been implemented yet. Until further enhancements, you may want to comment out all limiters, caching, token requirements, and certain routes (For the routes, there are ones with `'/<int:id>'` to comment in for testing).


## Project Structure

The application is organized as follows:

```
M1L5-Assignment/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── extensions.py
│   ├── blueprints/
│   │   ├── __init__.py
│   │   ├── customerAccounts/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── customers/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── inventory/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── invoices/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   │   └── schemas.py
│   │   ├── mechanicAccounts/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── mechanics/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── serviceItems/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   │   └── schemas.py
│   │   ├── serviceTickets/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── vehicles/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── ERD.drawio
│   │   ├── Mechanic Shop Endpoints.postman_collection.json
│   │   ├── util.py
│   │   └── validation_creation.py
├── PRIVATE.py
├── config.py
├── requirements.txt
└── app.py
```

- **app/**: Contains the main application package.
  - **__init__.py**: Initializes the Flask application and registers Blueprints.
  - **models.py**: Defines SQLAlchemy models and initializes the database.
  - **extensions.py**: Initializes extensions like Marshmallow.
  - Blueprint packages for each resource:
    -  **customerAccounts/**
    -  **customers/**
    -  **inventory/**
    -  **invoices/**
    -  **mechanicAccounts/**
    -  **mechanics/**
    -  **mechanicTickets/**
    -  **serviceItems/**
    -  **services/**
    -  **serviceTickets/**
    -  **vehicles/**
        - **__init__.py**: Initializes the Blueprint and imports routes.
        - **routes.py**: Contains route definitions for the Blueprint.
        - **schemas.py**: Defines Marshmallow schemas for the Blueprint's models.
- **PRIVATE.py**: Users must create this file to store database credentials (not included in the repository for security).
- **config.py**: Configuration settings for the application.
- **requirements.txt**: Lists Python dependencies.
- **app.py**: Entry point to run the application.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Tmiseray/MechMagicAutoWorx.git
   cd MechMagicAutoWorx
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a PRIVATE.py file**:

   In the root directory, create a `PRIVATE.py` file and add your database credentials:

   ```python
   secret_key_options = [
    "List multiple options",
    "Use a different secret depending on user",
    "This is best for authorization & security"
   ]
   MYDB = "your_database_name"
   MYPASSWORD = "your_password"
   CUSTOMERSECRET = secret_key_options[index]
   MECHANICSECRET = secret_key_options[index]
   ```

   For the index, it is your choice on how to set it. 
   For security purposes, you will want a different secret depending on the user.
   This file should not be committed to version control.

5. **Set up the database**:

   You will not need to manually create your database based on the models defined in `models.py`. The moment you run `app.py`, it creates all tables needed. Ensure your database connection details are correctly set in `PRIVATE.py`.

## Usage

1. **Run the application**:

   ```bash
   flask run
   ```

   The application will be accessible at `http://127.0.0.1:5000/`.

2. **API Endpoints**:

   - **CustomerAccount Endpoints** (`/customers/accounts`):
     - `POST /`: Create a new customer account.
     - `GET /all`: Retrieve all customer accounts.
     - `GET /<int:id>`: Retrieve a customer account by Customer ID.
     - `GET /`: Retrieve a customer account by customer's login details.
     - `PUT /<int:id>`: Update a customer account by Customer ID.
     - `DELETE /<int:id>`: Delete a customer account by Customer ID.
     - `POST /login`: Login for customer account.

   - **Customer Endpoints** (`/customers`):
     - `POST /`: Create a new customer.
     - `GET /all`: Retrieve all customers.
     - `GET /<int:id>`: Retrieve a customer by ID.
     - `PUT /<int:id>`: Update a customer by ID.
     - `DELETE /<int:id>`: Delete a customer by ID.

   - **Inventory Endpoints** (`/inventory`):
     - `POST /`: Create a new inventory.
     - `GET /all`: Retrieve all inventory.
     - `GET /<int:id>`: Retrieve an inventory by ID.
     - `PUT /<int:id>`: Update an inventory by ID.

   - **Invoice Endpoints** (`/customers/tickets/invoices`):
     - `POST /`: Create a new invoice.
     - `GET /all`: Retrieve all invoices.
     - `GET /<int:id>`: Retrieve a invoice by ID.
     - `PUT /<int:id>`: Update a invoice by ID.
     - `GET /my-invoices`: Customer can retrieve their own invoices.

   - **MechanicAccount Endpoints** (`/mechanics/accounts`):
     - `POST /`: Create a new mechanic account.
     - `GET /all`: Retrieve all mechanic accounts.
     - `GET /<int:id>`: Retrieve a mechanic account by Mechanic ID.
     - `GET /`: Retrieve a mechanic account by mechanic's login details.
     - `PUT /<int:id>`: Update a mechanic account by Mechanic ID.
     - `DELETE /<int:id>`: Delete a mechanic account by Mechanic ID.
     - `POST /login`: Login for mechanic account.

   - **Mechanic Endpoints** (`/mechanics`):
     - `POST /`: Create a new mechanic.
     - `GET /all`: Retrieve all mechanics.
     - `GET /<int:id>`: Retrieve a mechanic by ID.
     - `PUT /<int:id>`: Update a mechanic by ID.
     - `DELETE /<int:id>`: Delete a mechanic by ID.
     - `GET /top-mechanics`: Retrieve top mechanics ordered by mosst mechanic tickets.

   - **MechanicTicket Endpoints** (`/mechanics/tickets`):
     - `POST /`: Create a new mechanic ticket.
     - `GET /all`: Retrieve all mechanic tickets.
     - `GET /<int:id>`: Retrieve a mechanic ticket by ID.
     - `PUT /<int:id>`: Update a mechanic ticket by ID.

   - **ServiceItem Endpoints** (`/inventory/items`):
     - `POST /`: Create a new service item.
     - `GET /all`: Retrieve all service items.
     - `GET /<int:id>`: Retrieve a service item by ID.
     - `PUT /<int:id>`: Update a service item by ID.

   - **Service Endpoints** (`/services`):
     - `POST /`: Create a new service.
     - `GET /all`: Retrieve all services.
     - `GET /<int:id>`: Retrieve a service by ID.
     - `PUT /<int:id>`: Update a service by ID.

   - **ServiceTicket Endpoints** (`/customers/tickets`):
     - `POST /`: Create a new service ticket.
     - `GET /all`: Retrieve all service tickets.
     - `GET /<int:id>`: Retrieve a service ticket by ID.
     - `PUT /<int:id>`: Update a service ticket by ID.
     - `GET /my-tickets`: Customer can retrieve their own service tickets

   - **Vehicle Endpoints** (`/customers/vehicles`):
     - `POST /`: Create a new vehicle.
     - `GET /all`: Retrieve all vehicles.
     - `GET /<int:id>`: Retrieve a vehicle by VIN.
     - `PUT /<int:id>`: Update a vehicle by VIN.

***NOTE:*** Endpoints without DELETE functionality is for record keeping purposes. This ensures all of the records for those endpoints will not be removed in case of audit, taxes, and/or warranty disputes. As well as, certain routes are set with wrappers `@token_required` or `@mechanic_token_required`. This ensures that either only the specific customer or the specific mechanic can update or delete their own information and to limit the access to certain endpoints to only allow mechanic access.


## Postman Testing

A Postman collection is provided to test all endpoints. 
Import the `Mechanic Shop Endpoints.postman_collection.json` file into Postman to access pre-configured requests. 
This also includes saved responses from previous testing for reference.

## Contributing

1. **Fork the repository**.
2. **Create a new branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Commit your changes**:

   ```bash
   git commit -m 'Add some feature'
   ```

4. **Push to the branch**:

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a pull request**.

## Acknowledgements

- Flask documentation on [Blueprints](https://flask.palletsprojects.com/en/stable/blueprints/).
- Marshmallow-SQLAlchemy [documentation](https://marshmallow-sqlalchemy.readthedocs.io/).
