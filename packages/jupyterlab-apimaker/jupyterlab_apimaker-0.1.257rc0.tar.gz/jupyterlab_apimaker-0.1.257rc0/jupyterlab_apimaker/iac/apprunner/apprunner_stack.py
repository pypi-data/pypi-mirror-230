from aws_cdk import (
    core as cdk,
    aws_apprunner as apprunner    
)
from jupyterlab_apimaker.smce_vars import *

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class ApprunnerStack(cdk.Stack):
    def __init__(self, 
    scope: cdk.Construct, 
    construct_id: str,
    ecr_access_role_arn,
    image_id,api_owner,
    api_name,
    api_ver,
     **kwargs) -> None:
        api_info = "-".join([api_owner,api_name,api_ver])
        super().__init__(scope, construct_id,  stack_name=api_info,**kwargs)
        ecrrole = ecr_access_role_arn
        cfn_service = apprunner.CfnService(self, "apibakerCfnService",
        source_configuration=apprunner.CfnService.SourceConfigurationProperty(
            authentication_configuration=apprunner.CfnService.AuthenticationConfigurationProperty(
                access_role_arn=ecrrole #"ECRaccessRoleArn",
                ),
            auto_deployments_enabled=True,
            image_repository=apprunner.CfnService.ImageRepositoryProperty(
                image_identifier=image_id,
                image_repository_type="ECR",
                image_configuration = apprunner.CfnService.ImageConfigurationProperty(
                    port=PORT,
                ),
            ),
        ),      
        health_check_configuration=apprunner.CfnService.HealthCheckConfigurationProperty(
            healthy_threshold=1,
            interval=5,
            protocol="TCP",
            timeout=2,
            unhealthy_threshold=5
        ),
        instance_configuration=apprunner.CfnService.InstanceConfigurationProperty(
            instance_role_arn=APPRUNNER_ROLE
        ),
        # THIS WOULD BE VERY USEFUL FOR APIS THAT REQUIRED ACCESS TO OTHER AWS SERVICES
        # instance_configuration=apprunner.CfnService.InstanceConfigurationProperty(
        #     cpu="cpu",
        #     instance_role_arn="instanceRoleArn",
        #     memory="memory"
        # ),
        #THIS SHOULD BE USER+API+VER rlinan_iptagger_v1
        
        service_name=api_info,
        tags=[cdk.CfnTag(
            key="NotebookUser",
            value=api_owner
        )]
    )
