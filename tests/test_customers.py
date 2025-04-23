import unittest
from app import create_app
from app.models import db, Customer
from app.utils.util import encode_token, encode_mechanic_token


def get_auth_header(user_id=123):
    token = encode_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def get_mechanic_auth_header(user_id=321, role="Mechanic"):
    token = encode_mechanic_token(user_id, role)
    return {"Authorization": f"Bearer {token}"}


class TestCustomerRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_create_customer_valid(self):
        payload = {"name": "John Doe", "email": "john@example.com", "phone": "1234567890"}
        response = self.client.post('/customers', json=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")

    def test_create_customer_invalid(self):
        payload = {"name": "", "email": "bademail", "phone": "123"}
        response = self.client.post('/customers', json=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.json)

    def test_get_all_customers_with_auth(self):
        with self.app.app_context():
            db.session.add(Customer(name="Test", email="test@test.com", phone="1234567890"))
            db.session.commit()
        headers = get_mechanic_auth_header()
        response = self.client.get('/customers/all', headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_all_customers_unauthenticated(self):
        response = self.client.get('/customers/all', follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_get_single_customer_valid(self):
        with self.app.app_context():
            customer = Customer(name="Jane Doe", email="jane@test.com", phone="9876543210")
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id
        headers = get_mechanic_auth_header()
        response = self.client.get(f'/customers/{customer_id}', headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], "jane@test.com")

    def test_get_single_customer_invalid(self):
        headers = get_mechanic_auth_header()
        response = self.client.get('/customers/9999', headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_update_customer_valid(self):
        with self.app.app_context():
            customer = Customer(name="Update Me", email="update@test.com", phone="2222222222")
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id
        payload = {"name": "Updated Name", "email": "update@test.com", "phone": "3333333333"}
        headers = get_auth_header(customer_id)
        response = self.client.put('/customers/update', json=payload, headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['phone'], "3333333333")

    def test_update_customer_invalid_id(self):
        payload = {"name": "Ghost", "email": "ghost@test.com", "phone": "9999999999"}
        headers = get_auth_header(user_id=9999)
        response = self.client.put('/customers/update', json=payload, headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_delete_customer_valid(self):
        with self.app.app_context():
            customer = Customer(name="Delete Me", email="delete@test.com", phone="4444444444")
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id
        headers = get_auth_header(customer_id)
        response = self.client.delete('/customers/delete', headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully Deleted", response.json['message'])

    def test_delete_customer_invalid_id(self):
        headers = get_auth_header(user_id=9999)
        response = self.client.delete('/customers/delete', headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Invalid Customer ID", response.json['message'])

if __name__ == '__main__':
    unittest.main()
