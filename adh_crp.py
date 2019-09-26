'''adh_crp CRP wrapper for REST calls'''

import json
import adal

from restfns import do_delete, do_get, do_get_next, do_patch, do_post, do_put
from settings import COMP_API, get_rm_endpoint, get_auth_endpoint, get_resource_endpoint


def create_dhg(access_token, subscription_id, resource_group, dhg_name,
              az_name, location):
    '''Create dedicated host group.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        dhg_name (str): Name of the new dedicated host group.
        az_name (str): Availability zone name.
        location (str): Azure data center location. E.g. west us.

    Returns:
        HTTP response. JSON body of the dedicated host group properties.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/hostgroups/', dhg_name,
                        '?api-version=', COMP_API])
    dhg_body = {'location': location}
    if az_name is not None:
        dhg_body['zones'] = [az_name]    
    body = json.dumps(dhg_body)
    return do_put(endpoint, body, access_token)

def create_dh(access_token, subscription_id, resource_group, dhg_name,
              dh_name, dh_sku, location):
    '''Create dedicated host group.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        dhg_name (str): Name of the new dedicated host group.
        az_name (str): Availability zone name.
        location (str): Azure data center location. E.g. westus.

    Returns:
        HTTP response. JSON body of the dedicated host group properties.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/hostgroups/', dhg_name,
                        '/', dh_name,
                        '?api-version=', COMP_API])
    dhg_body = {'location': location}
    host_sku = {'name': dh_sku}    
    dhg_body['sku'] = host_sku   
    body = json.dumps(dhg_body)
    return do_put(endpoint, body, access_token)


def deallocate_vm(access_token, subscription_id, resource_group, vm_name):
    '''Stop-deallocate a virtual machine.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        vm_name (str): Name of the virtual machine.

    Returns:
        HTTP response.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/virtualMachines/', vm_name,
                        '/deallocate',
                        '?api-version=', COMP_API])
    return do_post(endpoint, '', access_token)


def get_compute_usage(access_token, subscription_id, location):
    '''List compute usage and limits for a location.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        location (str): Azure data center location. E.g. westus.

    Returns:
        HTTP response. JSON body of Compute usage and limits data.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/providers/Microsoft.compute/locations/', location,
                        '/usages?api-version=', COMP_API])
    return do_get(endpoint, access_token)


def get_vm(access_token, subscription_id, resource_group, vm_name):
    '''Get virtual machine details.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        vm_name (str): Name of the virtual machine.

    Returns:
        HTTP response. JSON body of VM properties.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/virtualMachines/', vm_name,
                        '?api-version=', COMP_API])
    return do_get(endpoint, access_token)


def get_vm_instance_view(access_token, subscription_id, resource_group, vm_name):
    '''Get operational details about the state of a VM.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        vm_name (str): Name of the virtual machine.

    Returns:
        HTTP response. JSON body of VM instance view details.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/virtualMachines/', vm_name,
                        '/InstanceView?api-version=', COMP_API])
    return do_get(endpoint, access_token)


def list_dhg(access_token, subscription_id, resource_group):
    '''List availability sets in a resource_group.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.

    Returns:
        HTTP response. JSON body of the list of availability set properties.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/hostgroups',
                        '?api-version=', COMP_API])
    return do_get_next(endpoint, access_token)


def list_dhg_sub(access_token, subscription_id):
    '''List dedicated host groups in a subscription.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.

    Returns:
        HTTP response. JSON body of the list of dedicated hostsproperties.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/providers/Microsoft.Compute/hostgroups',
                        '?api-version=', COMP_API])
    return do_get_next(endpoint, access_token)


def list_dh(access_token, subscription_id, resource_group,dhg_name):
    '''List dedicated hosts in a host group.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        dhg_name (str): Dedicated host group name.

    Returns:
        HTTP response. JSON body of the list of dedicated hosts properties.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/hostgroups/', dhg_name,
                        '/hosts'
                        '?api-version=', COMP_API])
    return do_get_next(endpoint, access_token)

def get_dh(access_token, subscription_id, resource_group,dhg_name, dh_name):
    '''Get a dedicated host and its instance view.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        dhg_name (str): Dedicated host group name.

    Returns:
        HTTP response. JSON body of the list of dedicated hosts properties.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/hostgroups/', dhg_name,
                        '/hosts,',dh_name,
                        '?$expand=instanceView&api-version=', COMP_API])
    return do_get_next(endpoint, access_token)



def list_vms(access_token, subscription_id, resource_group):
    '''List VMs in a resource group.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.

    Returns:
        HTTP response. JSON body of a list of VM model views.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/virtualMachines',
                        '?api-version=', COMP_API])
    return do_get(endpoint, access_token)


def list_vms_sub(access_token, subscription_id):
    '''List VMs in a subscription.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.

    Returns:
        HTTP response. JSON body of a list of VM model views.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/providers/Microsoft.Compute/virtualMachines',
                        '?api-version=', COMP_API])
    return do_get_next(endpoint, access_token)


def restart_vm(access_token, subscription_id, resource_group, vm_name):
    '''Restart a virtual machine.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        vm_name (str): Name of the virtual machine.

    Returns:
        HTTP response.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/virtualMachines/',
                        vm_name,
                        '/restart',
                        '?api-version=', COMP_API])
    return do_post(endpoint, '', access_token)


def start_vm(access_token, subscription_id, resource_group, vm_name):
    '''Start a virtual machine.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        vm_name (str): Name of the virtual machine.

    Returns:
        HTTP response.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/virtualMachines/',
                        vm_name,
                        '/start',
                        '?api-version=', COMP_API])
    return do_post(endpoint, '', access_token)


def stop_vm(access_token, subscription_id, resource_group, vm_name):
    '''Stop a virtual machine but don't deallocate resources (power off).

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        vm_name (str): Name of the virtual machine.

    Returns:
        HTTP response.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/virtualMachines/',
                        vm_name,
                        '/powerOff',
                        '?api-version=', COMP_API])
    return do_post(endpoint, '', access_token)


def update_vm(access_token, subscription_id, resource_group, vm_name, body):
    '''Update a virtual machine with a new JSON body. E.g. do a GET, change something, call this.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        vm_name (str): Name of the virtual machine.
        body (dict): JSON body of the VM.

    Returns:
        HTTP response.
    '''
    endpoint = ''.join([get_rm_endpoint(),
                        '/subscriptions/', subscription_id,
                        '/resourceGroups/', resource_group,
                        '/providers/Microsoft.Compute/virtualMachines/', vm_name,
                        '?api-version=', COMP_API])
    return do_put(endpoint, body, access_token)


def get_access_token(tenant_id, application_id, application_secret):
    '''get an Azure access token using the adal library.

    Args:
        tenant_id (str): Tenant id of the user's account.
        application_id (str): Application id of a Service Principal account.
        application_secret (str): Application secret (password) of the Service Principal account.

    Returns:
        An Azure authentication token string.
    '''
    context = adal.AuthenticationContext(
        get_auth_endpoint() + tenant_id, api_version=None)
    token_response = context.acquire_token_with_client_credentials(
        get_resource_endpoint(), application_id, application_secret)
    return token_response.get('accessToken')


def get_access_token_from_cli():
    '''Get an Azure authentication token from CLI's cache.

    Will only work if CLI local cache has an unexpired auth token (i.e. you ran 'az login'
        recently), or if you are running in Azure Cloud Shell (aka cloud console)

    Returns:
        An Azure authentication token string.
    '''

    # check if running in cloud shell, if so, pick up token from MSI_ENDPOINT
    if 'ACC_CLOUD' in os.environ and 'MSI_ENDPOINT' in os.environ:
        endpoint = os.environ['MSI_ENDPOINT']
        headers = {'Metadata': 'true'}
        body = {"resource": "https://management.azure.com/"}
        ret = requests.post(endpoint, headers=headers, data=body)
        return ret.json()['access_token']

    else: # not running cloud shell
        home = os.path.expanduser('~')
        sub_username = ""

        # 1st identify current subscription
        azure_profile_path = home + os.sep + '.azure' + os.sep + 'azureProfile.json'
        if os.path.isfile(azure_profile_path) is False:
            print('Error from get_access_token_from_cli(): Cannot find ' + azure_profile_path)
            return None
        with codecs.open(azure_profile_path, 'r', 'utf-8-sig') as azure_profile_fd:
            subs = json.load(azure_profile_fd)
        for sub in subs['subscriptions']:
            if sub['isDefault'] == True:
                sub_username = sub['user']['name']
        if sub_username == "":
            print('Error from get_access_token_from_cli(): Default subscription not found in ' +  \
                azure_profile_path)
            return None

        # look for acces_token
        access_keys_path = home + os.sep + '.azure' + os.sep + 'accessTokens.json'
        if os.path.isfile(access_keys_path) is False:
            print('Error from get_access_token_from_cli(): Cannot find ' + access_keys_path)
            return None
        with open(access_keys_path, 'r') as access_keys_fd:
            keys = json.load(access_keys_fd)

        # loop through accessTokens.json until first unexpired entry found
        for key in keys:
            if key['userId'] == sub_username:
                if 'accessToken' not in keys[0]:
                    print('Error from get_access_token_from_cli(): accessToken not found in ' + \
                        access_keys_path)
                    return None
                if 'tokenType' not in keys[0]:
                    print('Error from get_access_token_from_cli(): tokenType not found in ' + \
                        access_keys_path)
                    return None
                if 'expiresOn' not in keys[0]:
                    print('Error from get_access_token_from_cli(): expiresOn not found in ' + \
                        access_keys_path)
                    return None
                expiry_date_str = key['expiresOn']

                # check date and skip past expired entries
                if 'T' in expiry_date_str:
                    exp_date = dt.strptime(key['expiresOn'], '%Y-%m-%dT%H:%M:%S.%fZ')
                else:
                    exp_date = dt.strptime(key['expiresOn'], '%Y-%m-%d %H:%M:%S.%f')
                if exp_date < dt.now():
                    continue
                else:
                    return key['accessToken']

        # if dropped out of the loop, token expired
        print('Error from get_access_token_from_cli(): token expired. Run \'az login\'')
        return None