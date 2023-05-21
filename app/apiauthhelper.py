from flask import request
from werkzeug.security import check_password_hash
from .models import User
import base64
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        if check_password_hash(user.password, password):
            return user
        
@token_auth.verify_token
def verify_token(token):
    user = User.query.filter_by(apitoken=token).first()
    if user:
        return user

def basic_auth_required(func):
    def decorated(*arg, **kwargs):
        # before
        if "Authorization" in request.headers:
            val = request.headers['Authorization']
            
            protocol, encoded_version = val.split()
            if protocol == 'Basic':
                username_password = base64.b64decode(encoded_version.encode('ascii')).decode('ascii')

                username, password = username_password.split(':')
            else:
                return {
                    'status': 'not ok',
                    'message': "Please use Basic Authentication"
                }
        else:
            return {
                'status': 'not ok',
                'message': "Please include the header Authorization with Basic Auth"
            }
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                return func(user=user, *arg, **kwargs)
            else:
                return {
                    'status': 'not ok',
                    'message': "Incorrect password."
                }
        else:
            return {
                'status': 'not ok',
                'message': "That username does not exist."
            }
    decorated.__name__ = func.__name__
    return decorated

def token_auth_required(func):
    def decorated(*arg, **kwargs):
        # before
        if "Authorization" in request.headers:
            val = request.headers['Authorization']
            
            protocol, token = val.split()
            if protocol == 'Bearer':
                pass
            else:
                return {
                    'status': 'not ok',
                    'message': "Please use Token Authentication (Bearer Token)"
                }, 401
        else:
            return {
                'status': 'not ok',
                'message': "Please include the header Authorization with Token Auth using a Bearer Token"
            }, 401
        user = User.query.filter_by(apitoken=token).first()
        if user:
            return func(user=user, *arg, **kwargs)
        else:
            return {
                'status': 'not ok',
                'message': "That token does not belong to a valid user."
            }, 401
    decorated.__name__ = func.__name__
    return decorated