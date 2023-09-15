#!/usr/bin/env python
import boto3
from constructs import Construct
from cdk8s import App, Chart
from .imports import k8s

from .apprunner.app import create_apprunner


from .zappaiac.app import create_zappa_settings
import logging
import json
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

autodetectaccountnumber = boto3.client('sts').get_caller_identity().get('Account')
AWS_REGION = "us-east-1"
APILABELS = {}
KANIKO_CACHE_ARGS = "--cache=true --cache-copy-layers=true --cache-ttl=24h"
BASE_LOC = "."
AWS_ACCOUNT_NUMBER = autodetectaccountnumber
ECR_BASE=AWS_ACCOUNT_NUMBER+".dkr.ecr."+AWS_REGION+".amazonaws.com/apibaker:"
ECR_ACCESS_ROLE="arn:aws:iam::"+AWS_ACCOUNT_NUMBER+":role/service-role/AppRunnerECRAccessRole"
#the class needs to go inside iac.k8s and imports folder (used by cdk8s) also need to go inside iac.k8s
class BakingApiFlask(Chart):
    def __init__(self, scope: Construct, id: str, apidomain: str, apiname: str, apiver: str, baker: str, image_url: str, namespace: str ):
        super().__init__(scope, id)

        # define resources here
        apilabelvalue = "baker-"+baker+"-"+apiname
        applabel = {"app": apilabelvalue}
        label = {**applabel,**APILABELS}

        ingress_annotations = {"kubernetes.io/ingress.class": "alb",
        "alb.ingress.kubernetes.io/scheme": "internet-facing",
        "alb.ingress.kubernetes.io/target-type": "ip"}

        # notice that there is no assigment neccesary when creating resources.
        # simply instantiating the resource is enough because it adds it to the construct tree via
        # the first argument, which is always the parent construct.
        # its a little confusing at first glance, but this is an inherent aspect of the constructs
        # programming model, and you will encounter it many times.
        # you can still perform an assignment of course, if you need to access
        # atrtibutes of the resource in other parts of the code.

        
        k8s.KubeNamespace(self, 'bakers-namespace',
                    metadata=k8s.ObjectMeta(name=namespace))
        
        service_name = baker + "-" + apiname + "-srve"
        k8s.KubeService(self, 'bakers-service',
                    metadata=k8s.ObjectMeta(
                        labels=label,
                        namespace=namespace, 
                        name=service_name),
                    spec=k8s.ServiceSpec(
                    ports=[k8s.ServicePort(port=80, target_port=k8s.IntOrString.from_number(5000))],
                    selector=label))

        cont_name = apiname+"-cont"
        k8s.KubeDeployment(self, 'bakers-deployment',
                        metadata=k8s.ObjectMeta(labels=label,namespace=namespace),
                        spec=k8s.DeploymentSpec(
                            replicas=2,
                            selector=k8s.LabelSelector(match_labels=label),
                            template=k8s.PodTemplateSpec(
                                metadata=k8s.ObjectMeta(labels=label),
                                spec=k8s.PodSpec(containers=[
                                k8s.Container(
                                name=cont_name,
                                image=image_url,
                                ports=[k8s.ContainerPort(container_port=5000)])]))))
        solution_path="/"+apiname+"/"+baker+"/*"
        k8s.KubeIngress(self,"bakers-ingress",
            metadata=k8s.ObjectMeta(
                labels=label,
                namespace=namespace,
                annotations=ingress_annotations),
            spec=k8s.IngressSpec(
                rules=[k8s.IngressRule(
                    host=apidomain,
                    http=k8s.HttpIngressRuleValue(
                        paths=[k8s.HttpIngressPath(
                            path=solution_path,
                            path_type="ImplementationSpecific",
                            backend=k8s.IngressBackend(
                                service=k8s.IngressServiceBackend(
                                    name=service_name,
                                    port=k8s.ServiceBackendPort(number=80)
                                )))]))]
        )
        )
    
def create_iac(apidomain,apiname,apiver,baker,image_url,iactype="",yaml_loc=".",namespace="bakers"):
    #api_info = "-".join([baker,apiname,apiver])
    api_name_and_version = apiname+apiver
    k8s_iac_path = yaml_loc+'/k8s_iac/'
    apprunner_iac_path = yaml_loc+'/apprunner_iac/'
    cft_template_path = apprunner_iac_path+api_name_and_version+".json"
    zappa_iac_path = yaml_loc+'/apigateway_iac/'
    # Create Kubernetes IaC
    if not iactype or iactype== "k8s":
        appid = "baker-"+baker+"-"+apiname+"-"+apiver
        app = App(outdir=k8s_iac_path)
        BakingApiFlask(
            scope=app,
            id=appid,
            apidomain=apidomain,
            baker=baker,
            apiname=apiname,
            apiver=apiver,
            image_url=image_url,
            namespace=namespace)
        app.synth()
        logger.info(f"K8s IaC Created")
    # Create Apprunner IaC
    if not iactype or iactype == "apprunner":
        create_apprunner(
            ecr_access_role_arn=ECR_ACCESS_ROLE,
            image_id=image_url,
            api_owner=baker,
            api_name=apiname,
            api_ver=apiver,
            outdir=apprunner_iac_path)
            
            
    # Create Zappa (APIGW + Lambda) IaC
    if not iactype or iactype == "apigw":
        zappa_response = create_zappa_settings(
            apiname=apiname,
            apiver=apiver,
            region="us-east-1",
            yaml_loc=zappa_iac_path)
        if zappa_response:
            logger.info(f"Zappa IaC Created")
        else:
            logger.info(f"Zappa IaC found an issue and was not Created")



# example to use from API Baker code
# from iac import main
# main.create_iac(...)
# apidomain,
# the domain the customer wants to use for their APIs, 
# this info gets use in the ingress service so even if other dns records point to the same api, 
# the call only responds when using the specify domain. i.e if apidomain=baker.mysmce.com
# baker.mysmce.com/rlinan/v2/converter/netcdftozarr will work but not
# a10e4899fd7de4183a206e2e0243e156-214043847.us-west-2.elb.amazonaws.com/rlinan/converter/netcdftozarr will not
# if apidomain is * then it will answer queries addressed to any domain
# apiname, 
#   should be set as the name of the notebook or value provided by the user
# apiver, 
#   still not clear how to set this value, could be the timedate or could be user input
# baker,
#   is the jupyterhub auth user, (NOT Jovyan)
# image_url, 
#   the registry provided with the tags being the version somethng like registry/apiname:apiver
# namespace,
#   is the kubernetes namespace where to deploy the apis