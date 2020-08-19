import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'fsndjadg.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://localhost:5000/fsndcapstone'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Modeled primarily after Auth0 Quick Start documentation for Python
# implementation backend/API by Luciano Balmaceda at Auth0.com
def get_token_auth_header():
    # Retrieve authorization header from request, assign to variable
    header = request.headers.get("Authorization", None)
    # If header does not exist, raise class AuthError
    if not header:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                         "Authorization header is expected"}, 401)
    # Assign sections of header into new object
    header_parts = header.split()
    # If the first part of the header prats is not Bearer, raise AuthError
    if header_parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must start with"
                         " Bearer"}, 401)
    # If header is only one portion long, raise AuthError
    elif len(header_parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    # If there are more than two parts to the header, raise AuthError
    elif len(header_parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must be"
                         " Bearer token"}, 401)
    # Assign token poriton of header to variable
    token = header_parts[1]
    return token


def check_permissions(permission, payload):
    # Check for permissions value within the payload, raise AuthError if not
    if not payload:
        raise AuthError({"code": "missing_payload",
                         "description":
                         "No payload"},401)
    if not payload['permissions']:
        raise AuthError({"code": "missing_permissions",
                         "description":
                         "No permissions in payload"}, 401)
    # Validate that valid permission exists within permissions of payload
    if permission not in payload['permissions']:
        raise AuthError({"code": "insufficient_permission",
                         "description":
                         "Needed permission not in payload"}, 401)
    return True


def verify_decode_jwt(token):
    # Retrieve jwks.json file from Auth0 domain
    jsonurl = urlopen(f"https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    # Convert jsonurl to json value, assign to jwks variable
    jwks = json.loads(jsonurl.read())
    # Convert token to unverified header
    unverified_header = jwt.get_unverified_header(token)
    # If key id does not exist in header, raise AuthError
    if 'kid' not in unverified_header:
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization missing key id"}, 401)
    rsa_key = {}
    # Loop for all key values from the Auth0 Domain json file
    for key in jwks['keys']:
        # If the key id from the jwks file equals the header, then assign the
        # key values to the empty rsa_key dict
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            # Call jwt.decode() on the token and rsa_key using default
            # algorithms, our define audience, and our issuer domain
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f'https://{AUTH0_DOMAIN}/'
            )
            return payload
        # If the token is expired, raise AuthError
        except jwt.ExpiredSignatureError:
            raise AuthError({"code": "token_expired",
                             "description":
                             "Token is expired"}, 401)
        # If the claims are wrong for the audience or issuer, raise AuthError
        except jwt.JWTClaimsError:
            raise AuthError({"code": "invalid_claims",
                             "description":
                             "Please check the audience and issuer"}, 401)
        # Catch any additional errors as invalid header with AuthError
        except Exception:
            raise AuthError({"code": "invalid_header",
                             "description":
                             "Unable to parse authentication token"}, 401)

# Provided by Udacity
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
