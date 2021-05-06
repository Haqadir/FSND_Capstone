import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen

'''
login_url = https://hqadir-demo.us.auth0.com/authorize?audience=drinks_fs_demo&response_type=token&client_id=3ppuJcwYqIUBt6caNpsR01NP2JlMkho7&redirect_uri=https://127.0.0.1:8080/login-token
logout_url = r'https://hqadir-demo.us.auth0.com/v2/logout?client_id=3ppuJcwYqIUBt6caNpsR01NP2JlMkho7&returnTo=https://127.0.0.1:8080/logout'
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InBSdDQ5SkdjVUdqNmhSamJIcE52VSJ9.eyJpc3MiOiJodHRwczovL2hxYWRpci1kZW1vLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZmU3YjRmYjU2OTZhZTAwNzEyZTY2NWEiLCJhdWQiOiJkcmlua3NfZnNfZGVtbyIsImlhdCI6MTYwOTA1NDMzMSwiZXhwIjoxNjA5MDYxNTMxLCJhenAiOiIzcHB1SmN3WXFJVUJ0NmNhTnBzUjAxTlAySmxNa2hvNyIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0OmRyaW5rcy1kZXRhaWwiXX0.zTZHTF9_8D9ETGPuBWV3fLHZ8BRemxD0cCBSBWKnF0Rwa6OQNjv2YVveEtecsHFhA0lLqHtF9gOE_NYazxowjLgZuu7Y4aGQFm2OqRIKsMoNbxuMCwdDJyyjKzQsYbncHTZcY2uLtFAZhkMMlt-_qcdJpmBl6982LOtOr4qezlHxADgNFqRpkfn0vxlP3hT5pBlZ6FlCf8ZfDY6V_sNBKM6jf_LKKHo73AwRL6yM8QVT_76sY6pxREIY915OmNsHHMpuUongv4HkfbruXE5bG-2AeflTTyRG-nrRAHAQfXAlmikqFgRYOuTMu2x33Z9Bf41rASHaCB7TUXhq0I60xQ
'''
AUTH0_DOMAIN = 'hqadir-demo.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'drinks_fs_demo'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    tok = request.headers.get('Authorization',None)
    if not tok:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = tok.split(' ')
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    else:
        token = parts[1]
    
    return token

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    # we expect RBAC active in our application
    if 'permissions' not in payload:
        print(permission)
        print(payload)
        raise AuthError({
                            'code': 'invalid_claims',
                            'description': 'Permissions not included in JWT.'
                        }, 400)
    # compare role based permissions of user/app with the enpoint being accessed and what permissions are required
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission is not Assigned.'
        }, 403)
    return True

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    
    # GET THE DATA IN THE HEADER
    try:
        unverified_header = jwt.get_unverified_header(token)
    except:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)
    
    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    
    # Finally, verify!!!
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
        except:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)
    else:
        
        return ({'code':'Unkown Error',
                'description':'Unable to parse Json Web Token',
                'tok':token,
                'rsaky':rsa_key
            })
'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
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