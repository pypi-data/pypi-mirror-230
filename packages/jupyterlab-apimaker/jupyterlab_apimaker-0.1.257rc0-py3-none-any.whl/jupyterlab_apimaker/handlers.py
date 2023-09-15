import ast
import json
import logging
import os
import importlib.resources as pkg_resources
import re
import shutil
import requests
import tornado
from . import flask_app_components
from jupyter_server.base.handlers import APIHandler
from pathlib import Path
from typing import Dict, List, Optional
from .iac import main as iac_
# from jupyterlab_apimaker import db
from .utils import (
    upload_file,
    container_build_and_push,
    tardir,
    parse_bucket,
    apprunner_cft_deploy,
    get_api_containerimage_uri,
    get_apprunner_endpoint,
    create_tokens_db,
    create_master_db,
    get_all_function_names,
    get_function_url,
    get_job_status)
from jupyterlab_apimaker.smce_vars import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


app_py = '''\
from flask import Flask, jsonify, make_response
from flask_restful import Api
from TokenResource import HandleTokensResource
from UserFunctionResource import UserFunctionResource
from HealthResource import HealthResource

app = Flask(__name__)
api = Api(app)


@api.representation('application/json')
def output_json(body, status=200, headers=None):
    response = make_response(jsonify(body), status)
    response.headers['Content-Type'] = 'application/json'
    response.headers.extend(headers or {})
    return response


api.add_resource(HealthResource, '/health', resource_class_kwargs={'representations': {'application/json': output_json}})
api.add_resource(UserFunctionResource, '/<username>/<notebook_name>/<function_name>', resource_class_kwargs={'representations': {'application/json': output_json}})
api.add_resource(HandleTokensResource, '/<username>/<notebook_name>/<function_name>/auth', resource_class_kwargs={'representations': {'application/json': output_json}})


if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=5005, channel_timeout=900)
'''


user_resource = '''\
from flask import request
from flask_restful import Resource, reqparse
from decorators import require_user_apikey
<import_user_function>


class UserFunctionResource(Resource):
    def __init__(self, representations=None):
        self.representations = representations
        super(UserFunctionResource, self).__init__()

    @require_user_apikey
    def get(self):
        return <get_return>


    @require_user_apikey
    def post(self):
        <post_code>
        return result
'''


requirements = '''\
Flask
flask-restful
waitress
python-jose
<req_from_user_function>
'''


dockerfile = f'''\
FROM fjrivas/jh:py38slim-apibkr
USER root
WORKDIR /usr/src/app
COPY . .
RUN python3 fix_requirements.py
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EXPOSE 5005
ENV USERNAME_FLASK=<username>
CMD [ "python3", "app.py"]
'''

# db.Base.metadata.create_all(db.engine)
# nb_fname = ipynbname.name()
# nb_path = os.path.abspath('')


def parse_notebook_cell(source_code_cell: str) -> List[str]:
    source = ast.parse(source_code_cell, type_comments=True)
    return [node for node in ast.walk(source) if type(node) == ast.FunctionDef]


class ProcessNotebook(APIHandler):
    @tornado.web.authenticated
    def post(self):
        notebook_info: Dict = dict()
        notebook_functions: List = list()
        received_notebook = self.get_json_body()
        notebook_info['python_version'] = received_notebook['metadata']['language_info']['version']
        for cell in received_notebook['cells']:
            if cell['cell_type'] == 'code':
                is_def_like_function = self.parse_def_function(cell['source'])
                if is_def_like_function:
                    source = parse_notebook_cell(cell['source'])
                    if (len(source) > 0):
                        notebook_functions.append({'function_name': source[0].name,
                                                   'function_code': cell['source']})
        notebook_info['functions'] = notebook_functions if len(notebook_functions) else None
        self.finish(json.dumps(notebook_info))

    def parse_def_function(self, source_code: str) -> bool:
        return True if sum(1 for _ in re.finditer(r"def (\w+)\s*\((.*?)\)(.*?):", source_code, re.MULTILINE)) > 0 else False


class MakeAPI(APIHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            # TODO: I would like for selected function to be a list, comming from select widget (RERL)
            selected_function = self.get_json_body()
            function_name = selected_function['userCode']['function_name']
            function_code = selected_function['userCode']['function_code']
            notebook_name = selected_function['notebookName']
            domain = selected_function['domain']
            path_to_notebook = selected_function['pathToNotebook']
            api_version = selected_function['apiVersion'].replace("_", "-")
            logger.info(f"Notebook Name => {notebook_name}")
            logger.info(f"Path To Notebook => {path_to_notebook}")
            logger.info(f"API Domain => {domain}")
            logger.info(f"API Version => {api_version}")
            logger.info(f"Selected Function Name => {function_name}")
            logger.info(f"Selected Function Code => {function_code}")
            work_dir = os.path.abspath(os.getcwd())
            logger.info(f"Working directory => {work_dir}")
            base_path = Path("/".join([MAIN_PATH, notebook_name, function_name]))
            api_owner = self.get_current_user()['name'].replace(".", "-")
            user_function_path = base_path / 'app'
            logger.info(f"app path => {user_function_path}")
            logger.info(f"iac path => {base_path}")
            flask_app_components_files = pkg_resources.contents(flask_app_components)

            # 1. Create folder for the flask app
            user_function_folder_created = self.prepare_flask_directory(user_function_path)
            if not user_function_folder_created:
                self.finish(json.dumps({"body": 'Could not create the application folder.'}))
            logger.info(f"app folder created => {user_function_folder_created}")

            # 2. Create __init__.py
            create_init = self.create_files_for_user_function(user_function_path / '__init__.py')
            if not create_init:
                self.finish(json.dumps({"body": 'Could not create init.'}))
            logger.info(f"app folder to package => {create_init}")

            # 3. Create main.py and add user_function to it
            with open(user_function_path / 'main.py', 'w') as main_file:
                main_file.write(function_code.strip() + "\n")
            logger.info(f"app files created")

            # TODO: Here we will import the list of functions
            # 4. Edit app.py:
            #   4.1 Add 'from main import <function_name>'
            import_statement = f"from main import {function_name}"

            #   4.2 Create Help and Usage message
            get_message = self.create_help_and_usage_message(function_code.strip())
            #   4.3 Edit GET route: to show the server is up and running and also show the help of the function
            #   4.4 Edit POST route: to add username/function_name and accept the parameters needed for the function to work.
            # Preparing Flask App with the appropriate code
            substitution_values_app_py = {
                '<username>': self.get_current_user()['name'],
                '<notebook_name>': notebook_name,
                '<function_name>': function_name,
            }
            substitution_values_user_resource = {
                '<get_return>': f"\"The endpoint {self.get_current_user()['name']}/{function_name} has 2 methods: GET and POST. {get_message}\"",
                '<import_user_function>': import_statement,
                '<post_code>': self.create_code_for_user_function(function_name, function_code)
            }

            flask_app = self.multiple_replace(substitution_values_app_py, app_py)
            with open(user_function_path / 'app.py', 'w') as flask_app_file:
                flask_app_file.write(flask_app)
            logger.info(f"API code built")

            user_resource_content = self.multiple_replace(substitution_values_user_resource, user_resource)
            with open(user_function_path / 'UserFunctionResource.py', 'w') as user_resource_file:
                user_resource_file.write(user_resource_content)
            logger.info(f"User Resource Built")

            # List of local files to be copied to the app directory.
            local_files_lst = self.get_user_additional_local_files(function_code, os.path.dirname(path_to_notebook) + '/')
            logger.info(f"List of local files => {local_files_lst}")

            # Writing all the requirements needed for both user_function and Flask App.
            # Per default Flask is a requirement however user_function might have its own
            substitution_values_requirements = {
                '<req_from_user_function>': self.get_requirements_from_user_function(function_code, local_files_lst)
            }

            full_requirements = self.multiple_replace(substitution_values_requirements, requirements)
            with open(user_function_path / 'requirements.txt', 'w') as requirements_file:
                requirements_file.write(full_requirements)
            logger.info(f"Requirements files created ")

            # 5. Writing Dockerfile files
            substitution_values_dockerfile = {
                '<username>': self.get_current_user()['name']
            }

            full_dockerfile = self.multiple_replace(substitution_values_dockerfile, dockerfile)
            logger.info(f"Dockerfile => {full_dockerfile}")
            with open(user_function_path / 'Dockerfile', 'w') as dockerfile_file:
                dockerfile_file.write(full_dockerfile)
            logger.info(f"Dockerfile files created ")

            files_list = [f for f in flask_app_components_files]

            files_to_remove = ['__pycache__', '__init__.py']

            for ftr in files_to_remove:
                if ftr in files_list:
                    files_list.remove(ftr)

            for f in files_list:
                with pkg_resources.path(flask_app_components, f) as p:
                    logger.info(f"Copying Package Files => {p} to {user_function_path}")
                    shutil.copy(p, user_function_path / os.path.basename(p))
            
            # Copying local files if any
            for user_file in local_files_lst:
                logger.info(f"Copying Local Files => {user_file}")
                user_file_dirname = Path(os.path.dirname(user_file))
                ftcp = Path(os.path.basename(user_file))
                dtcp = Path(os.path.basename(os.path.dirname(user_file)))
                logger.info(f"File to Copy => {ftcp}")
                logger.info(f"Dir to Copy => {dtcp}")
                logger.info(f"Destination => {str(user_function_path / dtcp / ftcp)}")
                if not (user_function_path / dtcp).exists():
                    os.makedirs(user_function_path / dtcp)
                shutil.copy(user_file, user_function_path / dtcp / ftcp)   

            default_token_info = create_tokens_db(user_function_path, TOKENS_DB)

            logger.info(f"List of files of the User Function => {os.listdir(user_function_path)}")

            # 6. Upload a tar of the app code to s3 as the location for the deployment context
            # we only need this if we are going to deploy the API instead of just generating the IaC and API code
            app_name_and_version = notebook_name + api_version  # i.e. iptagger0_1
            app_tar_file_name = app_name_and_version + "_app.tar.gz"  # iptagger0_1_app.tar.gz
            app_tar_output = Path(base_path / app_tar_file_name)  # apibaker/iptagger/iptagger0_1_app.tar.gz
            app_tar_output_str = str(app_tar_output.resolve())  # "apibaker/iptagger/iptagger0_1_app.tar.gz"
            app_path = str(user_function_path.resolve())  # "apibaker/iptagger/app/"
            tardir(app_path, app_tar_output)
            logger.info(f"API app tar file created on Jupyter Notebook environment  {app_tar_output_str}")

            app_context = KKAPI_SOURCE_CONTEXT_BASE + notebook_name + "/" + app_tar_file_name  # ie. s3://smce-kaniko/iptagger/iptagger0_1_app.tar.gz
            app_dockerfile = KKAPI_SOURCE_DOCKERFILE  # this value is path in relation to context
            # , kanikapi does not support specifiying dockerfile location yet, so it left empty for now

            bucket_name = parse_bucket(app_context)["bucket_name"]  # ie. s3://smce-kaniko/
            app_key_name = parse_bucket(app_context)["key_name"]  # ie. iptagger/iptagger0_1_app.tar.gz
            if WITH_DEPLOYMENT:
                response_app = upload_file(app_tar_output_str, bucket_name, app_key_name)
                if not response_app:
                    logger.error(f"There has been an AWS \
                    Error uploading the KANIKAPI context files")
                else:
                    logger.info(f"API context files uploaded sucessfully to ==>{app_context}")

            # 7. Create a container image that contains the API code
            # We build and push a container image to registry using KanikAPI API. A SMCE API for Kaniko and other tasks
            if WITH_DEPLOYMENT:
                cont_build = container_build_and_push(
                    id_token=ID_TOKEN,
                    dockerfile=app_dockerfile,
                    context=app_context,
                    cregistry=KKAPI_REGISTRY,
                    kkapi_endpoint=KKAPI_ENDPOINT,
                    tag=app_name_and_version)
                logger.info(f"Cont Build JOB ID => {cont_build.text}")
                job_id = json.loads(cont_build.text)["job_id"]
                container_image_uri = get_api_containerimage_uri(
                    id_token=ID_TOKEN,
                    kkapi_endpoint=KKAPI_ENDPOINT,
                    job_id=job_id)
                logger.info(f"Kanikapi response {cont_build.text}")

            # 8. Creating IaC unless iactype is specify this code builds all the IaC for the type of deployments supported
            base_path_str = str(base_path.resolve())
            if WITH_DEPLOYMENT:
                image_url = container_image_uri
            else:
                image_url = "<replace with container_image_url>"
            iac_.create_iac(apidomain=domain,
                            apiname=notebook_name,
                            apiver=api_version,
                            baker=api_owner,
                            image_url=image_url,
                            yaml_loc=base_path_str,
                            iactype="")
            logger.info(f"IaC files created ")

            # 8. upload a tar file to s3 containing the AWS app runner code.
            # this location on s3 would be the context for the app runner deployment that would be use by kanikapi
            # we only need to do this if we are going to deploy

            apprunner_tar_file_name = app_name_and_version + "_apprunner.tar.gz"
            apprunner_tar_output = Path(base_path / apprunner_tar_file_name)
            apprunner_tar_output_str = str(apprunner_tar_output.resolve())
            apprunner_iac_path = base_path_str + '/apprunner_iac/'
            api_info = "-".join([api_owner, notebook_name, api_version])
            cft_template_path = api_info + ".template.json"

            tardir(apprunner_iac_path, apprunner_tar_output, 'app_runner')
            logger.info(f"apprunner IaC tar file created on Jupyter Notebook environment {apprunner_tar_output_str}")

            apprunner_context = KKAPI_SOURCE_CONTEXT_BASE + notebook_name + "/" + apprunner_tar_file_name
            apprunner_key_name = parse_bucket(apprunner_context)["key_name"]
            if WITH_DEPLOYMENT:
                response_apprunner = upload_file(apprunner_tar_output_str, bucket_name, apprunner_key_name)
                if not response_apprunner:
                    logger.error(f"There has been an AWS \
                    Error uploading the KANIKAPI context files")
                else:
                    logger.info(f"AWS App Runner context files uploaded sucessfully to ==>{apprunner_context}")

            # ======= DEPLOYMENT, THIS MAY BE BETTER TO GO SOMEWHERE ELSE, different library? ===========#

            # 9 Deploying infrastructure with AWS App Runner CFT
            if WITH_DEPLOYMENT:
                cft_context = "s3://" + "/".join([bucket_name, apprunner_key_name])
                deploy_cft_result = apprunner_cft_deploy(
                    id_token=ID_TOKEN,
                    kkapi_endpoint=KKAPI_ENDPOINT,
                    context=cft_context,
                    cft_template=cft_template_path,
                    stack_name=api_info)
                cft_job_id = json.loads(deploy_cft_result.text)["job_id"]
                # we can ask for the endpoint but since the deployment takes several minutes the endpoint value will be "unknown"
                # until the deployment is completed, therefore we may need to get this later to show in the API catalog
                ar_endpoint = get_apprunner_endpoint(id_token=ID_TOKEN, kkapi_endpoint=KKAPI_ENDPOINT, job_id=cft_job_id)

                logger.info(f"CFT Container created with this response => {deploy_cft_result}")
                logger.info(f"CFT Container created with this endpoint => {ar_endpoint}")

            if default_token_info:
                current_user = self.get_current_user()['name']
                apiURL = f"{ar_endpoint}/{current_user}/{notebook_name}/{function_name}"
                logger.info('Container Token DB File created')
                logger.info(f"API URL => {apiURL}")
                default_token_master_db = create_master_db(work_dir, MASTER_DB, notebook_name, function_name, apiURL)

                if default_token_master_db:
                    logger.info('Master Token DB File created')
        except OSError as exc:
            logger.info(f"There has been an OSError => {exc}")
        else:
            current_user = self.get_current_user()['name']
            self.finish(json.dumps({
                        "statusCode": 200,
                        "body": {
                            "url": f"{ar_endpoint}/{current_user}/{notebook_name}/{function_name}",
                            "defaultToken": default_token_info,
                            "jobId": cft_job_id
                        }
                        }))

    def prepare_flask_directory(self, flask_app_path: Path) -> Optional[bool]:
        try:
            os.makedirs(flask_app_path, exist_ok=True)
            # Do we really need to do this?
            os.chmod(flask_app_path, 0o777)
        except OSError as exc:
            print(f"Flask App Directory creation at: {flask_app_path}: {exc}")
            return None
        except IOError as exc:
            print(f"There has been an IOError => {exc}")
        else:
            return True


    def create_files_for_user_function(self, path_to_file: Path) -> None:
        try:
            with open(path_to_file, 'w'):
                pass
        except OSError as exc:
            print(f'Could not open the file {path_to_file}, {exc}')
            return None
        except IOError as exc:
            print(f'IOError: {exc}')
            return None
        else:
            return True


    def get_params_from_user_function(self, function_code: str) -> Optional[List]:
        user_function_params = [line.strip() for line in function_code.split("\n") if re.search("^param:", line.strip())]
        return user_function_params or None


    def get_help_from_user_function(self, function_code: str) -> Optional[List]:
        user_function_help = [line.strip() for line in function_code.split("\n") if re.search("^help:", line.strip())]
        return user_function_help or None


    def get_requirements_from_user_function(self, function_code: str, local_files_lst: List) -> str:
        source = ast.parse(function_code)
        imports = [im.name if '.' not in im.name else im.name.split('.')[0] for node in ast.walk(source) if type(node) == ast.Import for im in node.names]
        imports_from = [node.module if '.' not in node.module else node.module.split('.')[0] for node in ast.walk(source) if type(node) == ast.ImportFrom]
        imports_list = list(set(imports + imports_from))
        logger.info(f"Imports List => {imports_list}")
        logger.info(f"Local Files => {local_files_lst}")
        final = list(set([x for x in imports_list for d in local_files_lst if x+'.py' in str(d) or x in str(d)]) ^ set(imports_list))
        logger.info(f"Requirements list cleaned => {final}")

        return '\n'.join(final)


    def create_help_and_usage_message(self, function_code: str) -> str:
        params = self.get_params_from_user_function(function_code)
        f_help = self.get_help_from_user_function(function_code)
        functions = parse_notebook_cell(function_code)
        get_message = ''
        if params:
            get_message = f"This function expects {len(params)} {'parameter' if len(params) == 1 else 'parameters'}: "
            for param in params:
                get_message += f"{param.split(':')[1]}: {param.split(':')[2]} "
        elif len(functions[0].args.args) > 0:
            get_message = f"This function expects {len(functions[0].args.args)} {'parameter' if len(functions[0].args.args) == 1 else 'parameters'}: "
            get_message += ", ".join({param.arg for param in functions[0].args.args})
        else:
            get_message = f"This function expects no parameters. "

        if f_help:
            get_message += f". Usage and Help: {f_help[0].split(':')[1]}"
        else:
            get_message += f". No usage instructions or help has been provided for this function."
        return get_message


    def create_code_for_user_function(self, function_name: str, function_code=None) -> str:
        code = list()
        # Perhaps the user didn't specified documentation but the function takes parameters
        functions = parse_notebook_cell(function_code)
        for param in functions[0].args.args:
            code.append(f"{param.arg} = request.get_json()['{param.arg}']\n")
        if len(functions[0].args.args) >= 1:
            code.append(f"if not {param.arg}:\n")
            code.append(" " * 4 + "return ({'error': {'statusCode': 400, 'message': 'No input data provided'}}, 400) \n")
        code.append(f"result = {function_name}({', '.join([a.arg for a in functions[0].args.args])})\n")
        return (' ' * 8).join(code)


    def get_params_from_function_signature(self, function_code) -> str:
        code = list()
        # Perhaps the user didn't specified documentation but the function takes parameters
        functions = parse_notebook_cell(function_code)
        for param in functions[0].args.args:
            code.append(f"{param.arg}")
        return ', '.join(code)


    def get_user_additional_local_files(self, function_code: str, base_path: str) -> Optional[List]:
        logger.info(f"Base Path Received => {base_path}")
        logger.info(f"Files in the base path => {os.listdir(base_path)}")

        source = ast.parse(function_code, type_comments=True)
        extracted_expr = [node for node in ast.walk(source) if type(node) == ast.Expr]

        pre_requisites = ['sys', 'path', 'insert']
        extracted_path_inserts = []
        path_list_from_path_inserts = []
        path_inserts_verified = []
        user_function_files_list = []
        expression_attrs = []
        base_path = Path(base_path)

        only_expr_with_sys = [i for i in extracted_expr for t in ast.walk(ast.parse(i)) if isinstance(t, ast.Name) and t.id == 'sys']

        for i in only_expr_with_sys:
            for t in ast.walk(ast.parse(i)):
                if isinstance(t, ast.Constant) and not isinstance(t.value, int):
                    extracted_path_inserts.append(t.value)
                elif isinstance(t, ast.Name):
                    expression_attrs.append(t.id)
                elif isinstance(t, ast.Attribute):
                    expression_attrs.append(t.attr)
                else:
                    pass

        if not list(set(expression_attrs)).sort() == pre_requisites.sort():
            return None

        for x in extracted_path_inserts:
            if not (base_path / Path(x)).exists():
                if (base_path / Path(x + '.py')).exists():
                    path_inserts_verified.append(True)
                    path_list_from_path_inserts.append(base_path / Path(x + '.py'))
                else:
                    path_inserts_verified.append(False)
            else:
                path_inserts_verified.append(True)
                path_list_from_path_inserts.append(base_path / Path(x))

        if not (all(e == path_inserts_verified[0] for e in path_inserts_verified)):
            return None

        for x in path_list_from_path_inserts:
            if '.py' in str(x):
                user_function_files_list.append(x)
            user_function_files_list += list(x.rglob("*.py"))
        cleaned = [f for f in set(user_function_files_list) if '.ipynb_checkpoints' not in str(f)]

        return cleaned
        

    def multiple_replace(self, dict: Dict, text: str) -> str:
        regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
        return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text, re.MULTILINE)


class GetJobStatus(APIHandler):
    @tornado.web.authenticated
    def post(self):
        job_id = self.get_json_body()['jobId']
        status = get_job_status(ID_TOKEN, KKAPI_ENDPOINT, job_id)
        logger.info(f"Job Status => {status}")
        return status


class MasterTokensDBHander(APIHandler):
    @tornado.web.authenticated
    def get(self):
        work_dir = os.path.abspath(os.getcwd())
        logger.info(f"Working directory => {work_dir}")
        logger.info(f"Master Token DB Path => {os.path.join(work_dir, MASTER_DB)}")
        all_endpoints = get_all_function_names(os.path.join(work_dir, MASTER_DB))
        logger.info(f"All Tokens => {all_endpoints}")
        self.finish(json.dumps({
            "statusCode": 200,
            "all_endpoints": all_endpoints,
            "jwt": ID_TOKEN}))


class FunctionTokensListHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        function_name = self.get_json_body()['function_name']
        notebook_name = self.get_json_body()['notebook_name']
        logger.info(f"Function Name Received in Handler => {function_name}")
        logger.info(f"Notebook Name Received in Handler => {notebook_name}")
        work_dir = os.path.abspath(os.getcwd())
        function_url = get_function_url(os.path.join(work_dir, MASTER_DB), function_name, notebook_name)
        headers = {
            'Authorization': f"Bearer {ID_TOKEN}"
        }
        tokens_list = requests.get(f"{function_url['url']}/auth", headers=headers)
        logger.info(f"Tokens List from container => {tokens_list.text}")
        if tokens_list.status_code != 200:
            self.finish(json.dumps({
                "statusCode": tokens_list.status_code,
                "tokens_list": None}))
        else:
            self.finish(json.dumps({
                "statusCode": 200,
                "tokens_list": tokens_list.json()}))


class TokenOperationsHandler(APIHandler):
    @tornado.web.authenticated
    def put(self):
        refresh_token_info = self.get_json_body()
        logger.info(f"Received Data => {refresh_token_info}")
        logger.info(f"RowId => {refresh_token_info['item']['rowid']}")
        logger.info(f"URL => {refresh_token_info['url']}")
        logger.info(f"Token Name => {refresh_token_info['item']['name']}")
        headers = {
            'Authorization': f"Bearer {ID_TOKEN}",
            'Content-Type': 'application/json'
        }
        payload = json.dumps({"name": refresh_token_info['item']['name']})
        logger.info(f"Payload => {json.dumps(payload)}")
        logger.info(f"Headers => {headers}")
        logger.info(f"Complete URL => {refresh_token_info['url']}/auth?id={refresh_token_info['item']['rowid']}")
        updated = requests.put(f"{refresh_token_info['url']}/auth?id={refresh_token_info['item']['rowid']}", headers=headers, data=payload)
        logger.info(f"Updated Token => {updated.text}")
        self.finish(json.dumps({"statusCode": updated.status_code, "token_info": updated.text}))


    @tornado.web.authenticated
    def post(self):
        new_token_name = self.get_json_body()
        logger.info(f"New Token Name => {new_token_name}")
        headers = {
            'Authorization': f"Bearer {ID_TOKEN}",
            'Content-Type': 'application/json'
        }
        payload = json.dumps({ "name": new_token_name['token_name']})
        new_token_info = requests.post(f"{new_token_name['url']}/auth", headers=headers, data=payload)
        logger.info(f"New Token Info => {new_token_info.text}")
        self.finish(json.dumps({"statusCode": new_token_info.status_code,
                                "new_token_info": new_token_info.text}))


    @tornado.web.authenticated
    def delete(self):
        delete_token_info = self.get_json_body()
        logger.info(f"Received Data => {delete_token_info}")
        headers = {
            'Authorization': f"Bearer {ID_TOKEN}",
            'Content-Type': 'application/json'
        }
        logger.info(f"Complete URL => {delete_token_info['url']}/auth?id={delete_token_info['item']['rowid']}")
        payload = json.dumps({})
        deleted = requests.delete(f"{delete_token_info['url']}/auth?id={delete_token_info['item']['rowid']}", headers=headers, data=payload)
        self.finish(json.dumps({"statusCode": deleted.status_code}))


# class APICollection(APIHandler):
#     @tornado.web.authenticated
#     def get(self):
#         #server_root = self.get_query_argument('serverRoot', None)
#         # user = request.args.get('user')
#         result = dict()
#         result['statusCode'] = 200
#         result['projects'] = dict()

#         all_projects = db.session.query(db.Projects).all()
#         client = docker.from_env()
#         running_containers_list = client.containers.list(filters={'status':'running'})
#         paused_exited_containers_list = client.containers.list(filters={'status':'paused'}) + client.containers.list(filters={'status':'exited'})

#         running_containers = [c.image.tags[0] for c in running_containers_list if c.image.tags]
#         paused_exited_containers = [c.image.tags[0] for c in paused_exited_containers_list if c.image.tags]

#         images_list = [ap.image_tag for ap in all_projects]

#         available_projects = [ap for ap in all_projects if ap.image_tag in self.intersection(running_containers, images_list)]
#         unavailable_projects = [ap for ap in all_projects if ap.image_tag in self.intersection(paused_exited_containers, images_list)]
#         db.session.close()
#         self.finish(json.dumps({
#             "statusCode": 200,
#             "projects": {
#                 "available": db.Projects.serialize_list(available_projects),
#                 "unavailable": db.Projects.serialize_list(unavailable_projects)
#             }
#             }))
#         # sample_project_1 = db.Projects('frivas','add_numbers', 'frivas/add_numbers:latest', 'http://localhost:5005/frivas/add_numbers', 5005, 1)
#         # sample_project_2 = db.Projects('frivas','sub_numbers', 'frivas/sub_numbers:latest', 'http://localhost:5005/frivas/sub_numbers', 5005, 0)
#         # sample_project_3 = db.Projects('lrodrigues','div_numbers', 'frivas/div_numbers:latst', 'http://localhost:5005/frivas/div_numbers', 5005, 1)
#         # db.session.add(sample_project_1)
#         # db.session.add(sample_project_2)
#         # db.session.add(sample_project_3)
#         # db.session.commit()
#     def intersection(self, lst1: List, lst2: List) -> List:
#         temp = set(lst2)
#         lst3 = [value for value in lst1 if value in temp]
#         return lst3 """
