# ADH-Mng Managing Azure Dedicated hosts at scale

Customers may opt-in to use Azure Dedicated Hosts (ADH) for several reasons ranging from security isolation to maintenance control. Regardless of the reason, the existing ADH API force them to manually provision hosts and assign each VM to a host in an optimal way.

In the case where a customer will be looking for a large scale deployment (starting with less than 10 hosts), they won't be able to scale with the existing API given the overhead in managing the utilization and creation of their hosts.
While the team is committed to expand the ADH API with an implicit approach where host selection will be carried automatically by the platform, this functionality is not expected by ADH GA.

##ADH-Mng Goals and Principles
1. ADH-Mng is a thin, open source utility which enables customers to manage their isolated (dedicated) environment at the level of host groups. 
1. ADH-Mng solves the gap with the existing API by selecting the best host for a new VM, provisioning new hosts when required, and cleaning up the host group when hosts become empty.

- ADH-Mng is an open source utility, provided as-is. 
- ADH-Mng is created to be used interactively or hosted by the customer in their subscription (it is not a service hosted by Microsoft)
- ADH-Mng authentication/authorization is based on Azure service principals which the customer creates and manages.
- ADH-Mng is a thin wrapper over Azure REST APIs and has no dependencies in other Azure modules


## ADH-Mng Usage 
The following are samples for ADH-Mng usage as an interactive utility

### Analyze existing environment
Read all of the host groups and hosts in the subscription, build an object representation and save it to a local file for future use. 
** python examples\adh_mng.py analyze **

Read the topology in a single resource group
** python examples\adh_mng.py analyze --resourcegroup DH1-RG **

### Host Recommendation 
Recommend the best of for a VM somewhere 
** python adh_mng.py recommend -resourcegroup DH1-RG --size Standard_D8s_v3 ** 

Recommend the best of for a VM somewhere in the region
** python adh_mng.py recommend --resourcegroup DH1-RG -size Standard_D8s_v3 --location eastus2 ** 

Recommend the best of for a VM somewhere in an availability zone 
** python adh_mng.py recommend -resourcegroup DH1-RG --size Standard_D8s_v3 --location eastus2 --zone 2 ** 

Recommend the best of for a VM using fault domains
** python adh_mng.py recommend -resourcegroup DH1-RG --size Standard_D8s_v3 --location eastus2 --faultdomain 1 ** 

Recommend the best of for a VM somewhere in an availability zone and fault domain
** python adh_mng.py recommend -resourcegroup DH1-RG --size Standard_D8s_v3 --location eastus2 -zone 2  ** --faultdomain 1 


Note: This is not an official Microsoft library, just some REST wrappers to make it easier to call the Azure REST API. For the official Microsoft Azure library for Python please go here: <a href="https://github.com/Azure/azure-sdk-for-python">https://github.com/Azure/azure-sdk-for-python</a>.


## Authenticating using a Service Principal
For a semi-permanent/hardcoded way to authenticate, you can create a "Service Principal" for your application (an application equivalent of a user). Once you've done this you'll have 3 pieces of information: A tenant ID, an application ID, and an application secret. You will use these to create an authentication token. For more information on how to get this information go here: [Authenticating a service principal with Azure Resource Manager](https://azure.microsoft.com/en-us/documentation/articles/resource-group-authenticate-service-principal/). See also: [Azure Resource Manager REST calls from Python](https://msftstack.wordpress.com/2016/01/05/azure-resource-manager-authentication-with-python/). Make sure you create a service principal with sufficient access rights, like "Contributor", not "Reader".

## National/isolated cloud support
To use this library with national or isolated clouds, set environment variables to override the public default endpoints.

E.g. bash shell example for China..
``` 
  export AZURE_RM_ENDPOINT='https://management.chinacloudapi.cn'
  export AZURE_AUTH_ENDPOINT='https://login.chinacloudapi.cn/'
  export AZURE_RESOURCE_ENDPOINT='https://management.core.chinacloudapi.cn/'
```
