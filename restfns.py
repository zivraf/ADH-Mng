'''azurerm restfns - REST functions for adh-mng (reused from azurerm)'''

import platform
import pkg_resources  # to get version
import requests

from settings import json_acceptformat, json_only_acceptformat, xml_acceptformat, \
charset, dsversion_min, dsversion_max, xmsversion, ams_rest_endpoint

def get_user_agent():
    '''User-Agent Header. Sends library identification to Azure endpoint.
    '''
    #version = pkg_resources.require("adh_mng")[0].version
    version="1.0"
    user_agent = "python/{} ({}) requests/{} adh-mng/{}".format(
        platform.python_version(),
        platform.platform(),
        requests.__version__,
        version)
    return user_agent

def do_get(endpoint, access_token):
    '''Do an HTTP GET request and return JSON.

    Args:
        endpoint (str): Azure Resource Manager management endpoint.
        access_token (str): A valid Azure authentication token.

    Returns:
        HTTP response. JSON body.
    '''
    headers = {"Authorization": 'Bearer ' + access_token}
    headers['User-Agent'] = get_user_agent()
    return requests.get(endpoint, headers=headers).json()


def do_get_next(endpoint, access_token):
    '''Do an HTTP GET request, follow the nextLink chain and return JSON.

    Args:
        endpoint (str): Azure Resource Manager management endpoint.
        access_token (str): A valid Azure authentication token.

    Returns:
        HTTP response. JSON body.
    '''
    headers = {"Authorization": 'Bearer ' + access_token}
    headers['User-Agent'] = get_user_agent()
    looping = True
    value_list = []
    vm_dict = {}
    while looping:
        get_return = requests.get(endpoint, headers=headers).json()
        if not 'value' in get_return:
            return get_return
        if not 'nextLink' in get_return:
            looping = False
        else:
            endpoint = get_return['nextLink']
        value_list += get_return['value']
    vm_dict['value'] = value_list
    return vm_dict


def do_delete(endpoint, access_token):
    '''Do an HTTP GET request and return JSON.

    Args:
        endpoint (str): Azure Resource Manager management endpoint.
        access_token (str): A valid Azure authentication token.

    Returns:
        HTTP response.
    '''
    headers = {"Authorization": 'Bearer ' + access_token}
    headers['User-Agent'] = get_user_agent()
    return requests.delete(endpoint, headers=headers)


def do_patch(endpoint, body, access_token):
    '''Do an HTTP PATCH request and return JSON.

    Args:
        endpoint (str): Azure Resource Manager management endpoint.
        body (str): JSON body of information to patch.
        access_token (str): A valid Azure authentication token.

    Returns:
        HTTP response. JSON body.
    '''
    headers = {"content-type": "application/json", "Authorization": 'Bearer ' + access_token}
    headers['User-Agent'] = get_user_agent()
    return requests.patch(endpoint, data=body, headers=headers)


def do_post(endpoint, body, access_token):
    '''Do an HTTP POST request and return JSON.

    Args:
        endpoint (str): Azure Resource Manager management endpoint.
        body (str): JSON body of information to post.
        access_token (str): A valid Azure authentication token.

    Returns:
        HTTP response. JSON body.
    '''
    headers = {"content-type": "application/json", "Authorization": 'Bearer ' + access_token}
    headers['User-Agent'] = get_user_agent()
    return requests.post(endpoint, data=body, headers=headers)


def do_put(endpoint, body, access_token):
    '''Do an HTTP PUT request and return JSON.

    Args:
        endpoint (str): Azure Resource Manager management endpoint.
        body (str): JSON body of information to put.
        access_token (str): A valid Azure authentication token.

    Returns:
        HTTP response. JSON body.
    '''
    headers = {"content-type": "application/json", "Authorization": 'Bearer ' + access_token}
    headers['User-Agent'] = get_user_agent()
    return requests.put(endpoint, data=body, headers=headers)


def get_url(access_token, endpoint=ams_rest_endpoint, flag=True):
    '''Get Media Services Final Endpoint URL.
    Args:
        access_token (str): A valid Azure authentication token.
        endpoint (str): Azure Media Services Initial Endpoint.
        flag (bol): flag.

    Returns:
        HTTP response. JSON body.
    '''
    return do_ams_get_url(endpoint, access_token, flag)

