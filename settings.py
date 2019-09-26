'''settings.py - place to store constants for adh-mng'''
import os

#AMS Endpoints...
ams_auth_endpoint = 'https://wamsprodglobal001acs.accesscontrol.windows.net/v2/OAuth2-13'
ams_rest_endpoint = 'https://media.windows.net/API'

# public defaults for authentication and resource endpoints
AZURE_RM_ENDPOINT = 'https://management.azure.com'
AZURE_AUTH_ENDPOINT = 'https://login.microsoftonline.com/'
AZURE_RESOURCE_ENDPOINT = 'https://management.core.windows.net/'
GRAPH_RESOURCE_HOST = 'graph.microsoft.com'

BASE_API = '2016-06-01'
COMP_API = '2018-10-01'
DEPLOYMENTS_API = '2018-05-01'
RESOURCE_API = '2017-05-10'

# AMS Headers
json_only_acceptformat = "application/json"
json_acceptformat = "application/json;odata=verbose"
xml_acceptformat = "application/atom+xml"
batch_acceptformat = "multipart/mixed" 
xmsversion = "2.13"
dsversion_min = "3.0;NetFx"
dsversion_max = "3.0;NetFx"
charset = "UTF-8"


def get_rm_endpoint():
    '''Set Azure Resource Manager endpoint by environment variable, else return default value.

    These functions facilitate the use of national and isolated clouds by allowing endpoints to
    be set dynamically. The default settings, if no environment varibles are used,
    are for public cloud.
    '''
    rm_endpoint = os.environ.get('AZURE_RM_ENDPOINT')
    if rm_endpoint is None:
        return AZURE_RM_ENDPOINT
    else:
        return rm_endpoint


def get_auth_endpoint():
    '''Set Azure auth endpoint by environment variable, else return default value.
    '''
    auth_endpoint = os.environ.get('AZURE_AUTH_ENDPOINT')
    if auth_endpoint is None:
        return AZURE_AUTH_ENDPOINT
    else:
        return auth_endpoint


def get_resource_endpoint():
    '''Set Azure reosurce endpoint by environment variable, else return default value.
    '''
    resource_endpoint = os.environ.get('AZURE_RESOURCE_ENDPOINT')
    if resource_endpoint is None:
        return AZURE_RESOURCE_ENDPOINT
    else:
        return resource_endpoint

