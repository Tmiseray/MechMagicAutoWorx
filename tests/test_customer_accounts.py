import unittest
from app import create_app
from app.models import db, Customer, CustomerAccount
from app.utils.util import encode_token, encode_mechanic_token


def get_auth_header(user_id=123):
    token = encode_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def get_mechanic_auth_header(user_id=321, role="Mechanic"):
    token = encode_mechanic_token(user_id, role)
    return {"Authorization": f"Bearer {token}"}


class TestCustomerAccounts(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_create_customer_account_valid(self):
        with self.app.app_context():
            customer = Customer(name="Test User", email="user@test.com", phone="1234567890")
            db.session.add(customer)
            db.session.commit()
            customer_id = customer.id
        payload = {
            "customer_id": customer_id,
            "email": "account@test.com",
            "password": "securePassword123"
        }
        response = self.client.post('/customers/accounts', json=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 201)

    def test_create_customer_account_invalid(self):
        payload = {
            "customer_id": 9999,
            "email": "bad",
            "password": "short"
        }
        response = self.client.post('/customers/accounts', json=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_login_valid(self):
        with self.app.app_context():
            customer = Customer(name="Login User", email="login@test.com", phone="1234567890")
            account = CustomerAccount(email="login@test.com", password="validpass123", customer=customer)
            db.session.add_all([customer, account])
            db.session.commit()
        payload = {
            "email": "login@test.com",
            "password": "validpass123"
        }
        response = self.client.post('/customers/accounts/login', json=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("auth_token", response.json)

    def test_login_invalid(self):
        payload = {
            "email": "nonexistent@test.com",
            "password": "wrongpass"
        }
        response = self.client.post('/customers/accounts/login', json=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_get_customer_account_valid(self):
        with self.app.app_context():
            customer = Customer(name="Viewer", email="viewer@test.com", phone="1111111111")
            account = CustomerAccount(email="viewer@test.com", password="viewpass123", customer=customer)
            db.session.add_all([customer, account])
            db.session.commit()
            customer_id = customer.id
        headers = get_auth_header(customer_id)
        response = self.client.get('/customers/accounts/details', headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], "viewer@test.com")

    def test_get_customer_account_invalid(self):
        headers = get_auth_header(9999)
        response = self.client.get('/customers/accounts/details', headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_get_all_customer_accounts_with_auth(self):
        with self.app.app_context():
            db.session.add(Customer(name="Test", email="test@test.com", phone="1234567890"))
            db.session.commit()
        headers = get_mechanic_auth_header()
        response = self.client.get('/customers/accounts/all', headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_all_customer_accounts_unauthenticated(self):
        response = self.client.get('/customers/accounts/all', follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_update_customer_account_valid(self):
        with self.app.app_context():
            customer = Customer(name="Updater", email="updater@test.com", phone="9999999999")
            account = CustomerAccount(email="updater@test.com", password="initialpass", customer=customer)
            db.session.add_all([customer, account])
            db.session.commit()
            customer_id = customer.id
        headers = get_auth_header(customer_id)
        payload = {"email": "updated@test.com", "password": "newsecurepass"}
        response = self.client.put('/customers/accounts/update', json=payload, headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_customer_account_valid(self):
        with self.app.app_context():
            customer = Customer(name="Deleter", email="deleter@test.com", phone="8888888888")
            account = CustomerAccount(email="deleter@test.com", password="deletepass123", customer=customer)
            db.session.add_all([customer, account])
            db.session.commit()
            customer_id = customer.id
        headers = get_auth_header(customer_id)
        response = self.client.delete('/customers/accounts/delete', headers=headers, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully Deleted", response.json['message'])


if __name__ == '__main__':
    unittest.main()
