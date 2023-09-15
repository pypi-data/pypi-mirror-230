import boto3
import contextlib
import json
import logging
import os
import requests
import secrets
import sqlite3
import tarfile
from botocore.exceptions import ClientError
from datetime import datetime
from typing import List, Tuple, Union, TypedDict
from time import sleep
from urllib.parse import urlparse


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TokenData(TypedDict):
    token: str
    name: str
    status: str
    created: str
    expires: str


class EndpointData(TypedDict):
    function_name: str
    url: str


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logger.error(f"Upload_file_error => {e}")
        return False
    return True


def container_build_and_push(id_token, dockerfile, context, cregistry, kkapi_endpoint, tag):
    # Kaniko supports specifiying a different path for the dockerfile, and Kanikapi may implement that in the future
    # the same for container registry
    id_token = id_token.replace('"', "")
    kkapi_query = kkapi_endpoint + "/create-containers?context=" + context + "&tag=" + tag
    logger.info(f"Calling Kanikapi API => {kkapi_query}")
    response = requests.post(kkapi_query, headers={'Authorization': 'Bearer ' + id_token})
    return response


def apprunner_cft_deploy(id_token, kkapi_endpoint, context, cft_template, stack_name):
    id_token = id_token.replace('"', "")
    payload = {'cft_context': context, 'cft_template': cft_template, 'cfstack_name': stack_name}
    cft_query = kkapi_endpoint + "/cft-deploy"
    logger.info(f"Calling Kanikapi API => {cft_query} with this parameters {payload}")
    response = requests.post(cft_query, data=payload, headers={'Authorization': 'Bearer ' + id_token})
    return response


def get_api_containerimage_uri(id_token, kkapi_endpoint, job_id):
    id_token = id_token.replace('"', "")
    jobid_query = kkapi_endpoint + "/curi?job_id=" + job_id
    response = requests.get(jobid_query, headers={'Authorization': 'Bearer ' + id_token})
    # response is like this "uri":"306565948140.dkr.ecr.us-east-1.amazonaws.com/apibaker:astro80_1"}\n'
    containerimage_uri = json.loads(response.text)["uri"]
    return containerimage_uri


def get_job_status(id_token, kkapi_endpoint, job_id):
    """This function will return the status of a kanikapi job.
    Kanikapi launches pod or jobs on a K8S to do things like build a container image and upload to registry or deploy a
    cloudformation template
    Args:
        id_token ([type]): [description]
        kkapi_endpoint ([type]): [description]
        job_id ([type]): [description]
    """

    id_token = id_token.replace('"', "")
    jobid_query = kkapi_endpoint + "/cstatus?job_id=" + job_id
    response = requests.get(jobid_query, headers={'Authorization': 'Bearer ' + id_token})
    # response is like this "uri":"306565948140.dkr.ecr.us-east-1.amazonaws.com/apibaker:astro80_1"}\n'
    job_status = json.loads(response.text)["status"]
    return job_status


def get_apprunner_endpoint(id_token, kkapi_endpoint, job_id):
    """This function will return the apprunner deployment endpoint url.
    Kanikapi launches pod or jobs on a K8S to do things like build a container image and upload to registry or deploy a
    cloudformation template
    Args:
        id_token ([type]): [description]
        kkapi_endpoint ([type]): [description]
        job_id ([type]): [description]
    """
    endpoint = ""
    id_token = id_token.replace('"', "")
    jobid_query = kkapi_endpoint + "/get_ar_endpoint?job_id=" + job_id
    logger.info(f"ID Token => {id_token}")
    logger.info(f"JOB ID Query => {jobid_query}")
    MAX_RETRIES = 10
    BACKOFF_FACTOR = 1
    for retry in range(1, MAX_RETRIES + 1):
        response = requests.get(jobid_query, headers={'Authorization': 'Bearer ' + id_token})
        logger.info(f"Response Raw => {response.text}")
        if is_json(response.text):
            if response.json()['endpoint'] and response.json()['endpoint'] != 'unknown':
                endpoint = response.json()['endpoint']
                logger.info(f"There is an endpoint => https://{endpoint}")
                break
        response.close()
        sleep(BACKOFF_FACTOR * (2 ** (retry)))
    logger.info(f"Response from KanikAPI => https://{endpoint}")
    # response is like this "uri":"306565948140.dkr.ecr.us-east-1.amazonaws.com/apibaker:astro80_1"}\n'
    return "https://" + endpoint


def is_json(request_response: str) -> bool:
    try:
        json.loads(request_response)
    except json.decoder.JSONDecodeError as e:
        return False
    except ValueError as e:
        return False
    else:
        return True


def flatten(tarinfo):
    tarinfo.name = os.path.basename(tarinfo.name)
    return tarinfo


def tardir(path, tar_name, tar_type='app'):
    with tarfile.open(tar_name, "w:gz") as tar_handle:
        for root, dirs, files in os.walk(path):
            for file in files:
                if tar_type == 'app':
                    logger.info(f"Root + File => {os.path.join(root, file)}")
                    logger.info(f"Root => {os.path.join(root.split('app')[-1:][0].replace('/','',1), file)}")
                    tar_handle.add(os.path.join(root, file), arcname=os.path.join(root.split('app')[-1:][0].replace('/','',1), file))
                else:
                    tar_handle.add(os.path.join(root, file), filter=flatten)


def parse_bucket(path_string):
    bucket_name = path_string.split("//")[1].split('/')[0]
    key_name = path_string.split("//")[1].replace(bucket_name, "")[1:]
    return {"bucket_name": bucket_name, "key_name": key_name}


def db_connection_handler(db_location: str, query: str, params: Tuple[str] = None) -> Union[TokenData, bool]:
    query_results = ''
    with contextlib.closing(sqlite3.connect(db_location)) as con:
        con.row_factory = sqlite3.Row
        with con as cur:
            if params:
                query_results = cur.execute(query, params)
            else:
                query_results = cur.execute(query)

            if 'select' in query.lower():
                query_results = [dict(t) for t in query_results.fetchall()]

    return query_results


def create_tokens_db(destination: str, filename: str) -> Union[bool, TokenData]:
    try:
        # Initial Token Information
        token = secrets.token_urlsafe(20)
        created = datetime.now()
        status = 'enabled'
        name = 'Default'
        db_location = os.path.join(destination, filename)

        # Creating tokens.db to be copied to the container
        query = '''CREATE TABLE IF NOT EXISTS tokens
                    (name text not null unique,
                    token text not null,
                    status text not null,
                    created text not null,
                    expires text)'''
        _ = db_connection_handler(db_location, query)

        query = '''SELECT rowid, * from tokens'''
        get_all_tokens = db_connection_handler(db_location, query)

        if (len(get_all_tokens) == 0):
            query = "INSERT INTO tokens(name, token, status, created, expires) VALUES (?, ?, ?, ?, ?)"
            params = (name, token, status, created.strftime('%s'), None,)
            _ = db_connection_handler(db_location, query, params)

        query = '''SELECT rowid, * from tokens'''
        all_tokens = db_connection_handler(db_location, query)
    except sqlite3.Error as e:
        logger.error(f"There has been an error creating the {filename}. {e}")
        return False
    else:
        return all_tokens


def create_master_db(destination: str,
                     filename: str,
                     notebook_name: str,
                     function_name: str,
                     apiURL: str) -> bool:
    try:
        logger.info(f"Notebook Name => {notebook_name}")
        logger.info(f"Function Name => {function_name}")
        logger.info(f"Endpoint URL => {apiURL}")
        db_location = os.path.join(destination, filename)

        query = '''CREATE TABLE IF NOT EXISTS endpoints
                    (notebook_name text not null,
                    function_name text not null,
                    url text not null)'''
        _ = db_connection_handler(db_location, query)

        query = '''select rowid, * from endpoints where function_name = ? and notebook_name = ?'''
        params = (function_name, notebook_name,)
        function_already_exists = db_connection_handler(db_location, query, params)
        if (len(function_already_exists) == 0):
            query = "INSERT INTO endpoints(notebook_name, function_name, url) VALUES (?, ?, ?)"
            params = (notebook_name, function_name, apiURL,)
            _ = db_connection_handler(db_location, query, params)
    except sqlite3.Error as e:
        logger.error(f"There has been an error creating the {filename} db with error: {e}")
        return False
    else:
        return True


def get_all_function_names(db_path: str) -> Union[bool, EndpointData]:
    try:
        healthy_endpoints = []
        query = '''select rowid, * from endpoints'''
        all_endpoints = db_connection_handler(db_path, query)
        for endpoint in all_endpoints:
            parsed_url = urlparse(endpoint['url'])
            logger.info(f"Endpoint URL => {parsed_url.scheme}://{parsed_url.netloc}/health")
            try:
                if requests.request('GET', parsed_url.scheme + '://' + parsed_url.netloc + '/health').status_code == 200:
                    healthy_endpoints.append(endpoint)
            except requests.exceptions.RequestException as error:
                pass
        logger.info(f"Content of All Endpoints => {all_endpoints}")
        logger.info(f"Healthy Endpoints => {healthy_endpoints}")
    except sqlite3.Error as e:
        logger.error(f"There has been an error querying master db with error: {e}")
        return False
    else:
        return healthy_endpoints


def get_function_url(db_path: str, function_name: str, notebook_name: str) -> Union[bool, List[str]]:
    try:
        query = '''select url from endpoints where function_name = ? and notebook_name = ?'''
        params = (function_name, notebook_name,)
        function_url = db_connection_handler(db_path, query, params)
        logger.info(f"Function URL => {function_url}")
        logger.info(f"Function Name => {function_name}")
    except sqlite3.Error as e:
        logger.error(f"There has been an error querying master db with error: {e}")
        return False
    else:
        return function_url[0]
