""" 
Example of the zappa_setting.json that I have to create
{
    "dev": {
        "app_function": "apigwlambda.app.app",
        "aws_region": "us-east-1",
        "profile_name": "default",
        "project_name": "downloads",
        "runtime": "python3.8",
        "s3_bucket": "zappa-2a10b361w"
    }
} 
"""
import string
import random
import json
import logging
import os
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
def create_zappa_settings(apiname, apiver, region, yaml_loc ):
    N = 7
    # using random.choices()
    # generating random strings 
    res = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k = N))
    bucket_name = "".join(["apibaker-",apiname,"-",res]).lower()
    zappa_settings_dict={}
    authorizer= {
    "type": "COGNITO_USER_POOLS",
    "provider_arns": [
    "arn:aws:cognito-idp:us-east-1:206660019955:userpool/us-east-1_L9uAf100N"
        ]
    }
    zappa_settings_dict[apiver] = {
        "app_function": "apigwlambda.app.app",
        "aws_region": region,
        "project_name": apiname,
        "runtime": "python3.8",
        "s3_bucket": bucket_name,
        "authorizer": authorizer
    }

    # TODO: Note that authorizer is hard-coded, needs to be offer it as an option
    zp_dep_file = yaml_loc+"zappa_settings.json"
    zappa_settings_json=json.dumps(zappa_settings_dict)
    
    if not os.path.exists(yaml_loc):
        os.makedirs(yaml_loc)
    try:
        with open(zp_dep_file, 'w') as outfile:
            outfile.write(zappa_settings_json)
        return True
    except OSError as exception:
        logger.error(f"Error creating IaC for Zappa {exception}")
        print(exception)
        return False