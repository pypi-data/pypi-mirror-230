import os
import secrets
import sqlite3
from datetime import datetime, timedelta
from flask_restful import Resource, reqparse, request
from typing import Union
from custom_types import TokenData, ErrorResponse
from db_utils import db_connection_handler
from decorators import require_admin_apikey


class HandleTokensResource(Resource):
    def __init__(self, representations=None):
        self.representations = representations
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=str, help='Id of the Token to be revoked or refreshed')
        self.parser.add_argument('name', type=str, help='Title to identify the token')
        super(HandleTokensResource, self).__init__()


    @require_admin_apikey
    def get(self):
        all_tokens = self.get_all_tokens()
        return all_tokens


    @require_admin_apikey
    def post(self):
        name = self.parser.parse_args()['name']
        if not name or name == '':
            return ({'error': {
                    'statusCode': 400,
                    'message': 'A token must have a name'}}, 400)
        token = self.create_new_token(name)
        if not token:
            return ({'error': {
                    'statusCode': 400,
                    'message': 'Error creating the token. Please contact the administrator.'
                    }}, 400)
        return token


    @require_admin_apikey
    def delete(self):
        token_id = self.parser.parse_args()['id']
        deleted = self.delete_token(token_id)
        return deleted


    @require_admin_apikey
    def put(self):
        token_id = self.parser.parse_args()['id']
        token_data = request.get_json(force=True)
        print(f"Token ID = {token_id}")
        print(f"Token Data => {token_data}")
        if not token_id:
            return 'Please provide a valid token id', 400
        if token_data is None:
            return 'Please provide a valid token data.', 400
        updated = self.update_token(token_id, token_data)
        print(f"Updated Token => {updated}")
        return updated


    def get_all_tokens(self) -> TokenData:
        query = '''SELECT rowid, * from tokens'''
        tokens = db_connection_handler(query)
        return [dict(t) for t in tokens]


    def create_new_token(self, name: str) -> Union[TokenData, ErrorResponse, bool]:
        try:
            token = secrets.token_urlsafe(20)
            created = datetime.now()
            expires = (created + timedelta(60))
            status = 'enabled'

            query = "INSERT INTO tokens(name, \
                                        token, \
                                        status, \
                                        created, \
                                        expires) VALUES (?, ?, ?, ?, ?)"
            params = (name, token, status, created.strftime('%s'), expires.strftime('%s'))
            _ = db_connection_handler(query, params)

            query = '''SELECT rowid, * from tokens where token=?'''
            new_token_info = db_connection_handler(query, (token,))
            print(f"New Token => {new_token_info}")

            if not new_token_info:
                raise sqlite3.Error
        except sqlite3.IntegrityError as e:
            print(f"Error => {e.args}")
            return {'error': {
                    'statusCode': 400,
                    'message': f"There is a token named {name} already. Please insert a unique name." if 'unique' in ' '.join(e.args).lower() else f"{e}"
                    }}, 400
        except sqlite3.Error as e:
            print(f"Error => {e.args}")
            return {'error': {
                    'statusCode': 400,
                    'message': f"There has been an error creating the new token => {e}"
                    }}, 400
        else:
            return {"statusCode": 200, "body": dict(new_token_info[0])}


    def delete_token(self, token_id: int) -> Union[TokenData, ErrorResponse, bool]:
        try:
            query = '''SELECT rowid, * from tokens where rowid=?'''
            token_found = db_connection_handler(query, (token_id,))

            if len(token_found) == 1:
                print(f"Token Found => {token_found}")
                if (token_found[0]['name'] == 'Default'):
                    raise CantDeleteDafultTokenError
                _ = db_connection_handler('''delete from tokens where rowid=?''', (token_id,))
            else:
                raise TokenNotFoundError
        except sqlite3.Error as e:
            print(f"Error => {e}")
            return {'error': {
                    'statusCode': 400,
                    'message': f"{e}"
                    }}, 400
        except CantDeleteDafultTokenError as e:
            return {'error': {
                    'statusCode': 400,
                    'message': f"{e}"
                    }}
        except TokenNotFoundError as e:
            return {'error': {
                    'statusCode': 400,
                    'message': f"{e}"
                    }}, 400
        else:
            return '', 204


    def update_token(self, token_id: int, token_data: TokenData = None) -> Union[TokenData, ErrorResponse, bool]:
        try:
            query = '''SELECT rowid, * from tokens where rowid=?'''
            token_found = db_connection_handler(query, (token_id,))

            if len(token_found) == 1:
                status = token_data['status'] if token_data.get('status') is not None else token_found[0]['status']
                token = secrets.token_urlsafe(20)
                created = datetime.now()
                if (token_found[0]['name'] == 'Default'):
                    name = 'Default'
                    expires = None
                else:
                    name = token_data['name'] if token_data.get('name', None) is not None else token_found[0]['name']
                    expires = (created + timedelta(60))            

                query = "update tokens SET token = ?, name = ?, status = ?, created = ?, expires = ? where rowid = ?"
                params = (token, name, status, created.strftime('%s'), expires.strftime('%s') if expires else None, token_id,)
                _ = db_connection_handler(query, params)
                query = '''SELECT rowid, * from tokens where name = ?'''
                updated_token_info = db_connection_handler(query, (name,))
            else:
                raise TokenNotFoundError
        except sqlite3.Error as e:
            print(f"Error => {e}")
            return {'error': {
                    'statusCode': 400,
                    'message': f"{e}"
                    }}, 400
        except TokenNotFoundError as e:
            print(f"Error => {e}")
            return {'error': {
                    'statusCode': 400,
                    'message': f"{e}"
                    }}, 400
        else:
            return dict(updated_token_info[0]), 200


class Error(Exception):
    pass


class CantDeleteDafultTokenError(Error):
    def __init__(self, message="Default token can't be deleted."):
        self.message = message
        super().__init__(self.message)


class TokenNotFoundError(Error):
    def __init__(self, message="The token id you have provided doesn't exist."):
        self.message = message
        super().__init__(self.message)
