
from PRIVATE import CUSTOMERSECRET, MECHANICSECRET
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from jose import jwt, exceptions
import bcrypt


# --------------------------------------------
# Customer Token
# --------------------------------------------

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split(" ")

            if len(parts) != 2 or parts[0] != "Bearer":
                return jsonify({'message': 'Invalid Authorization header format!'}), 401

            token = parts[1]

            try:
                data = jwt.decode(token, CUSTOMERSECRET, algorithms=['HS256'])
                user_id = data['sub']
                
            except exceptions.ExpiredSignatureError:
                return jsonify({'message': 'Token has expired!'}), 401
            except exceptions.JWTError:
                return jsonify({'message': 'Invalid token!'}), 401

            return f(user_id, *args, **kwargs)
        
        else:
            return jsonify({'message': 'You must be logged in to access this area!'}), 401

    return decorated


def encode_token(user_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(user_id)
    }

    token = jwt.encode(payload, CUSTOMERSECRET, algorithm='HS256')
    return token



# --------------------------------------------
# Mechanic Token
# --------------------------------------------

def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            parts = auth_header.split(" ")

            if len(parts) != 2 or parts[0] != "Bearer":
                return jsonify({'message': 'Invalid Authorization header format!'}), 401

            token = parts[1]

            try:
                data = jwt.decode(token, MECHANICSECRET, algorithms=['HS256'])
                user_id = data['sub']
                role = data['role']
                
            except exceptions.ExpiredSignatureError:
                return jsonify({'message': 'Token has expired!'}), 401
            except exceptions.JWTError:
                return jsonify({'message': 'Invalid token!'}), 401

            return f(user_id, role, *args, **kwargs)
        
        else:
            return jsonify({'message': 'You must be a mechanic to access this area!'}), 401

    return decorated


def encode_mechanic_token(user_id, role):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(user_id),
        'role': role
    }

    token = jwt.encode(payload, MECHANICSECRET, algorithm='HS256')
    return token


# --------------------------------------------
# Password Hashing & Verification
# --------------------------------------------


def hash_password(password):
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return hashed_password.decode('utf-8')


def check_password(password, hashed_password):

    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
