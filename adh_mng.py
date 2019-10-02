'''create_vmss.py - simple program to do an imperative VMSS quick create from a platform image'''
import argparse
import json
import sys
import logging
import pickle
import uuid

from adh_return import *
from adh_crp import *
from adh_cache import *


log_format = " %(asctime)s [%(levelname)s] %(message)s"
logger = logging.getLogger('example')
logging.basicConfig(format=log_format, level=logging.DEBUG)
default_chache_filename = 'adhcache.txt'

def main():
    '''Main routine.'''
    # validate command line arguments
    arg_parser = argparse.ArgumentParser(prog='dhg_mng')
    arg_parser.add_argument('cmd', action='store',choices=['analyze', 'recommend', 'create-host'], help = "cmd command to perform")

    arg_parser.add_argument('--host', '-hn', required=False, action='store', help='Name of the dedicated host')
    arg_parser.add_argument('--resourcegroup', '-r', action='store', required=False, help='resource-group limit to a specific resource group')
    arg_parser.add_argument('--location', '-l', action='store', required=False, help='Location, e.g. eastus')
    arg_parser.add_argument('--zone', '-z', action='store', required=False, help='Availability zone 1,2, or 3')
    arg_parser.add_argument('--faultdomain', '-fd', action='store', required=False, help='Platform fault domain 0,1, or 2')
    arg_parser.add_argument('--size', '-s', action='store', required=False, help='VM size like Standard_D2s_v3')
    arg_parser.add_argument('--hostgroup', '-hg', required=False,help='name of the host group')
    arg_parser.add_argument('--hostcount', '-hc', required=False,help='number of hosts to create')
    arg_parser.add_argument('--sku', '-sk', required=False, action='store', help='sku select a host sku e.g. DSv3_Type1')
    arg_parser.add_argument('--verbose', '-v', action='store_true', default=False,
                            help='Print operational details')
    args = arg_parser.parse_args()
    logger.debug ("dhg_mng utility")

    command = args.cmd
    location = args.location
    host_group = args.hostgroup
    resource_group = args.resourcegroup
    zone = args.zone
    faultDomain = args.faultdomain
    host_name = args.host
    vm_size = args.size
    host_sku = args.sku
    host_count = args.hostcount

    
    # Load Azure app defaults
    try:
        with open('azurermconfig.json') as config_file:
            config_data = json.load(config_file)
    except FileNotFoundError:
        returnObj.code = -1
        returnObj.message = "Expecting azurermconfig.json in current folder"
        return returnObj

        #logger.error ("Expecting azurermconfig.json in current folder")
        #sys.exit()

    tenant_id = config_data['tenantId']
    app_id = config_data['appId']
    app_secret = config_data['appSecret']
    subscription_id = config_data['subscriptionId']

    # authenticate
    access_token = get_access_token(tenant_id, app_id, app_secret)

    if command =='analyze':
        logger.debug ("Analyze a DHG:Enter")
        return analyze_dhg (access_token, subscription_id, location, resource_group, host_group)
        
    elif command =='recommend':
        logger.debug ("Recommend VM placement:Enter")
        if not vm_size:
            return ADH_Return(-1,"VM size is a required parameter for VM recomendation")
        if not location:
            return ADH_Return(-1,"A location is a required parameter for VM recomendation")

        return recommend_vm_placement (access_token, subscription_id, location, zone, faultDomain, vm_size, resource_group, host_group)
        
    elif command == 'create-host':
        logger.debug ("create-host VM placement:Enter")
        create_host (access_token, subscription_id, location, zone, host_sku, resource_group, host_group, host_name, host_count)
        logger.debug ("create-host VM placement:Exit")
    else:
        logger.warn ("Unsupported operation")
   
def analyze_dhg (access_token, subscription_id,location, resource_group, host_group):
    '''Analyze a Dedicated Host Group.

    Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        location (str): Azure region. E.g. westus.
        host_group (str): A specific dedicated host group to analyze (optional)

    Returns:
        Object representation of the dedicated host group.
    '''

    logger.debug ("dhg_mng : analyze_dhg.")
    local_cache = DedicateHostCache()
    '''Refactor
    if not resource_group:
        dhg_list = list_dhg_sub(access_token, subscription_id)
        vm_list = list_vms_sub(access_token,subscription_id)
    elif resource_group  and not host_group:
        dhg_list = list_dhg(access_token, subscription_id,resource_group)
        vm_list = list_vms(access_token,subscription_id,resource_group)
    else:
        logger.warn ("dhg_mng : analyze_dhg nunsupported parameters")
        return ADH_Return (-1,'analyze_dhg nunsupported parameters')
    if 'error' in dhg_list:
        logger.warn ("dhg_mng : analyze_dhg returned error:"+dhg_list['error']['code'])
        return ADH_Return (-1,'analyze_dhg internal error')
    local_cache.populate_host_groups(dhg_list,access_token, subscription_id, resource_group)

    vm_dictionary={}
    for vm in vm_list['value']:
        vm_dictionary[vm['id'].upper()]=vm
    
    local_cache.update_vm_info(vm_dictionary)
    '''
    returnObj= local_cache.build_cache (access_token, subscription_id,location, resource_group, host_group)
    if returnObj.code ==0:
        filehandler = open (default_chache_filename,'wb')
        pickle.dump (local_cache,filehandler)
        filehandler.close()
    return returnObj

def recommend_vm_placement (access_token, subscription_id, location, zone, faultDomain, vm_size, resource_group, host_group):
    '''Recommend a VM placement in a dedicated host.

        Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        location (str): Azure region. E.g. westus.
        zone (int): Potential Availability Zone (optional)
        faultDomain: Platform fault domain
        vm_size (str): The size of the VM we wish to place 
        host_group (str): A specific dedicated host group to analyze (optional)

        Returns:
        The Id of the best host which can fit the desired VM size.
    '''

    logger.debug ("dhg_mng : recommend_vm_placement : Enter.")
    local_cache = DedicateHostCache()
    local_cache = pickle.load ( open (default_chache_filename,'rb'))

    candidate_host_dictionary = {}

    for host_grp_id, host_grp in local_cache.host_group_list.items():
        if location and (host_grp.location != location):
            logger.debug ("Host group %s does not match location setting", host_grp.name)
            continue
        if zone and (host_grp.az != zone):
            logger.debug ("Host group %s does not match zone setting", host_grp.name)
            continue
        if host_group and (host_group.lower() != host_grp.name.lower()):
            logger.debug ("Host group %s does not match host group ", host_grp.name)
            continue 
        if (resource_group and host_grp.resource_group.lower() != resource_group.lower()):
            logger.debug ("Host group %s does not match resource group setting %s", host_grp.resource_group,resource_group)
            continue
        for host_id, host in host_grp.host_list.items():
            if faultDomain and faultDomain != host.fault_domain:
                logger.debug ("Host  %s does not fault domain parameter %s", host.id,faultDomain)
                continue
            host_ranking = host.rank_allocation (vm_size)
            if host_ranking >0:
                candidate_host_dictionary[host.id]=host_ranking
    
    best_host = Host()

    if len(candidate_host_dictionary) > 0:
        best_rank = 0.0
        for host, ranking in candidate_host_dictionary.items():
            if ranking > best_rank:
                best_host = host
                best_rank = ranking
                logger.debug ("found new candidate. Rank %d, HostId %s", best_rank, best_host)

        logger.debug ("\n\nBest Host is %s", best_host)
        returnObj = ADH_Return(0,"Success")        
        returnObj.body = best_host 
        return returnObj
    
    logger.debug ("No hosts are available for this VM size")
    host_sku = SKUS().host_sku_for_vm_size(vm_size)
    if host_sku is None:
        return ADH_Return(-1,"Required VM size is not supported.")          
    if host_group is None:
        return ADH_Return(-1,"A Host group is required to create a host.")          
    if resource_group is None:
        return ADH_Return(-1,"A Resource group is required to create a host.")          

    host_name = host_group+str(uuid.uuid4())[:6]    
    hostReturnStr = create_dh(access_token, subscription_id, resource_group, host_group,host_name, host_sku, location)

    if hostReturnStr.status_code == 201:
        new_host = get_dh (access_token,subscription_id,resource_group,host_group,host_name)
        returnObj= ADH_Return(0 ,"Success")  
        returnObj.body = new_host["id"]
        return returnObj

    return ADH_Return(-1,"Failed to create a host")        

    

def create_host (access_token, subscription_id, location, zone, faultDomain, sku, resource_group, host_group, host_name, host_count):
    '''Grow the host group by adding hosts.

        Args:
        access_token (str): A valid Azure authentication token.
        subscription_id (str): Azure subscription id.
        resource_group (str): Azure resource group name.
        location (str): Azure region. E.g. westus.
        zone (int): Potential Availability Zone (optional)
        hostgroup (str): The name of the group to grow
        host_name (str): A name for a host to create
        sku (str): A host SKU to create
        count (int): How many hosts to create

        Returns:
        A return code 
    '''
    if  location is None or sku is None or resource_group is None or host_group is None:
        logger.warn ("create_host: Mandatory parameters are location, zone, resource_group, host_group")
        return ADH_Return(-1,"create_host: Mandatory parameters are location, zone, resource_group, host_group") 
        
    if sku not in SKUS.host_skus:
        logger.warn ("create_host: unsupported host sku %s", sku)
        return ADH_Return(-1,"create_host: unsupported host sku") 
    if host_name is None:
        host_name = host_group + uuid.uuid1().urn[-6:]

    return create_dh(access_token, subscription_id, resource_group, host_group,host_name, sku, location)

if __name__ == "__main__":
    returnObj = main()
    if returnObj.code !=0:
        sys.stderr.write (returnObj.message)
    else:
        sys.stdout.write (returnObj.body)
    sys.exit(returnObj.code)
