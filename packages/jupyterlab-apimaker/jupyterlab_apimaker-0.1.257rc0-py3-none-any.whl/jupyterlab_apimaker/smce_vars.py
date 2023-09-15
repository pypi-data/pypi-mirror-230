import os

PORT = "5005"
MAIN_PATH = "apibaker"
ID_TOKEN = os.environ["ID_TOKEN"].replace('"', "")
KKAPI_SOURCE_CONTEXT_BASE = "s3://smce-kaniko/"
# This is the name of the dockerfile in relation to the context, kanikapi assumes
# Dockerfile on the root of the context when no passed
KKAPI_SOURCE_DOCKERFILE = ""
KKAPI_REGISTRY = ""
KKAPI_ENDPOINT = 'https://eoj6aun62i.execute-api.us-east-1.amazonaws.com/dev/'
WITH_DEPLOYMENT = True
MASTER_DB = '.apibaker_default_tokens.db'
TOKENS_DB = 'tokens.db'
APPRUNNER_ROLE = "arn:aws:iam::306565948140:role/APIBakerOnAPPRunner"
