# AzureDH (azurerm barnch)
Easy to use Python library for Azure Resource Manager.

The azurerm library provides wrapper functions for the Azure REST api. It doesn't include every option for every API call but it is easy to extend. The goal is to make it easy to call the API from Python using the latest API versions (in some cases before the official SDKs are available).

Note: This is not an official Microsoft library, just some REST wrappers to make it easier to call the Azure REST API. For the official Microsoft Azure library for Python please go here: <a href="https://github.com/Azure/azure-sdk-for-python">https://github.com/Azure/azure-sdk-for-python</a>.

## Latest news
For what's new in the most recent version refer to the [Changelog](https://github.com/gbowerman/azurerm/blob/master/changelog.md).

For occasional azurerm code samples and announcements see the [azurerm blog](https://msftstack.wordpress.com/?s=azurerm).

## Installation
1. pip install azurerm . If you make local changes ot the azurerm folder, call local build/install : python setup.py install --user
2. To call these functions you need an authentication token. One way to get this is by creating a Service Principal, another is to get a bearer token using CLI. 

## Authenticating using a Service Principal
For a semi-permanent/hardcoded way to authenticate, you can create a "Service Principal" for your application (an application equivalent of a user). Once you've done this you'll have 3 pieces of information: A tenant ID, an application ID, and an application secret. You will use these to create an authentication token. For more information on how to get this information go here: [Authenticating a service principal with Azure Resource Manager](https://azure.microsoft.com/en-us/documentation/articles/resource-group-authenticate-service-principal/). See also: [Azure Resource Manager REST calls from Python](https://msftstack.wordpress.com/2016/01/05/azure-resource-manager-authentication-with-python/). Make sure you create a service principal with sufficient access rights, like "Contributor", not "Reader".

## Authenticating using CLI
When you run a CLI command, it caches an authentication token which you can use with azurerm calls. Recent versions of CLI have a command which returns an authentication token: _az account get-access-token_. Azurerm has added a new function to get the Azure authentication token from CLI's local cache: 
```
azurerm.get_access_token_from_cli()
```
This saves you from having to create a Service Princial at all. Note: This function will fail unless you have an unexpired authentication token in your local CLI cache. I.e. you have run _az login_ on the same machine recently.

Example authenticating using the Azure Portal Cloud Shell:
```
me@Azure:-$ pip install --user --upgrade azurerm
me@azure:-$ python
>>> import azurerm
>>> token = azurerm.get_access_token_from_cli()
>>> azurerm.list_subscriptions(token)
```

## azurerm examples
See below for some simple examples. A detailed set of **azurerm** programming examples can be found here: [azurerm Python library programming examples](https://github.com/gbowerman/azurerm/blob/master/examples.md). For more examples look at the [azurerm examples library](https://github.com/gbowerman/azurerm/tree/master/examples). 

For full documentation see [azurerm reference manual](https://github.com/gbowerman/azurerm/tree/master/docs).

See also the unit test suite which covers the main storage, network, compute functions - the goal is to expand it to test every function in the library: [test](https://github.com/gbowerman/azurerm/tree/master/test)

### National/isolated cloud support
To use this library with national or isolated clouds, set environment variables to override the public default endpoints.

E.g. bash shell example for China..
``` 
  export AZURE_RM_ENDPOINT='https://management.chinacloudapi.cn'
  export AZURE_AUTH_ENDPOINT='https://login.chinacloudapi.cn/'
  export AZURE_RESOURCE_ENDPOINT='https://management.core.chinacloudapi.cn/'
```

#### Example to list Azure subscriptions, create a Resource Group, list Resource Groups
```
import azurerm

# create an authentication token (use a Service Principal or call get_access_token_from_cli())
# Service principal example:
tenant_id = 'your-tenant-id'
application_id = 'your-application-id'
application_secret = 'your-application-secret'

access_token = azurerm.get_access_token(tenant_id, application_id, application_secret)

# list subscriptions
subscriptions = azurerm.list_subscriptions(access_token)
for sub in subscriptions['value']:
    print(sub['displayName'] + ': ' + sub['subscriptionId'])

# select the first subscription
subscription_id = subscriptions['value'][0]['subscriptionId']

# create a resource group
print('Enter Resource group name to create.')
rgname = input()
location = 'southeastasia'
rgreturn = azurerm.create_resource_group(access_token, subscription_id, rgname, location)
print('Create RG return code: ' + str(rgreturn.status_code)

# list resource groups
resource_groups = azurerm.list_resource_groups(access_token, subscription_id)
for rg in resource_groups['value']:
    print(rg["name"] + ', ' + rg['location'] + ', ' + rg['properties']['provisioningState'])
``` 

#### Example to create a virtual machine
See [create_vm.py](https://github.com/gbowerman/azurerm/tree/master/examples/create_vm.py).

See also an example to create a VM Scale Set [create_vmss.py](https://github.com/gbowerman/azurerm/tree/master/examples/create_vmss.py).

#### Example to create a Media Services Account
See [createmediaserviceaccountinrg.py](https://github.com/gbowerman/azurerm/tree/master/examples/createmediaserviceaccountinrg.py)

## Functions currently supported
A basic set of infrastructure create, list, query functions are implemented. If you want to add something please send me a PR (don't forget to update this readme too).

See the [Function reference](https://github.com/gbowerman/azurerm/tree/master/docs) for full documentation.