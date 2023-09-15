from db_utils import db_connection_handler
from jose import jwt


def verify_user_token(token: str) -> bool:
    query = '''SELECT rowid, * from tokens where token=?'''
    token_found = db_connection_handler(query, (token,))
    if len(token_found) == 0:
        return False
    return True


def verify_admin_token(token: str, username: str) -> bool:
    if get_username_from_token(token) != username:
        return False
    return True


def get_username_from_token(token):
    """
    Get unverified token expected cognito username from claims
    :param token: string with cognito JWT
    :return: string with username; None if unable to identify the username
    """
    claims = jwt.get_unverified_claims(token)

    use = claims["token_use"]
    if use == "id":
        return claims["cognito:username"]
    if use == "access":
        return claims["username"]
    return None
