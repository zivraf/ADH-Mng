'''create_vmss.py - simple program to do an imperative VMSS quick create from a platform image'''
import argparse
import json
import sys
import logging
import pickle

from adh_crp import *
from adh_cache import *


# from haikunator import Haikunator

log_format = " %(asctime)s [%(levelname)s] %(message)s"
logger = logging.getLogger('example')
logging.basicConfig(format=log_format, level=logging.DEBUG)
default_chache_filename = 'adhcache.txt'

class ADH_Return:
    def __init__(self):            
        self.code = 0
        self.message = ""
        self.body = ""

def main():
    '''Main routine.'''
    # validate command line arguments
    arg_parser = argparse.ArgumentParser(prog='dhg_mng')
    arg_parser.add_argument('cmd', action='store',choices=['analyze', 'recommend', 'create-host'], help = "cmd command to perform")

    arg_parser.add_argument('--host', '-hn', required=False, action='store', help='Name of the dedicated host')
    arg_parser.add_argument('--capacity', '-c', required=False, action='store', help='Number of VMs')
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
    capacity = args.capacity
    host_group = args.hostgroup
    reosurce_group = args.resourcegroup
    zone = args.zone
    faultDomain = args.faultdomain
    host_name = args.host
    vm_size = args.size
    host_sku = args.sku
    host_count = args.hostcount

    returnObj = ADH_Return()

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
        local_cache = analyze_dhg (access_token, subscription_id, location, reosurce_group, host_group)
        logger.debug ("Analyze a DHG:Exit")
    elif command =='recommend':
        logger.debug ("Recommend VM placement:Enter")
        if not vm_size:
            returnObj.code = -1
            returnObj.message = "VM size is a required parameter for VM recomendation"
            return returnObj

            #logger.error ("Recommend VM placement: VM size is a required parameter")
            #sys.exit()   
        if (not location and (zone or faultDomain)):
            logger.error ("Recommend VM placement: You need to specify region to use")
            sys.exit()     
        recommendation = recommend_vm_placement (access_token, subscription_id, location, zone, faultDomain, vm_size, reosurce_group, host_group)
        logger.debug ("Recommend VM placement:Exit")
    elif command == 'create-host':
        logger.debug ("create-host VM placement:Enter")
        create_host (access_token, subscription_id, location, zone, host_sku, reosurce_group, host_group, host_name, host_count)
        logger.debug ("create-host VM placement:Exit")
    else:
        logger.warn ("Unsupported operation")
   
def analyze_dhg (access_token, subscription_id,location, reosurce_group, host_group):
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
    if not reosurce_group:
        dhg_list = list_dhg_sub(access_token, subscription_id)
        vm_list = list_vms_sub(access_token,subscription_id)
    elif reosurce_group  and not host_group:
        dhg_list = list_dhg(access_token, subscription_id,reosurce_group)
        vm_list = list_vms(access_token,subscription_id,reosurce_group)
    else:
        logger.warn ("dhg_mng : analyze_dhg nunsupported parameters")
        return
    if 'error' in dhg_list:
        logger.warn ("dhg_mng : analyze_dhg returned error:"+dhg_list['error']['code'])
        return
    local_cache.populate_host_groups(dhg_list,access_token, subscription_id, reosurce_group)

    vm_dictionary={}
    for vm in vm_list['value']:
        vm_dictionary[vm['id'].upper()]=vm
    
    local_cache.update_vm_info(vm_dictionary)
    filehandler = open (default_chache_filename,'wb')
    pickle.dump (local_cache,filehandler)
    filehandler.close()

    return local_cache

def recommend_vm_placement (access_token, subscription_id, location, zone, faultDomain, vm_size, reosurce_group, host_group):
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
    for host_group_id, host_group in local_cache.host_group_list.items():
        if location and (host_group.location != location):
            logger.debug ("Host group %s does not match location setting", host_group.name)
            continue
        if zone and (host_group.az != zone):
            logger.debug ("Host group %s does not match zone setting", host_group.name)
            continue
        if (reosurce_group and host_group.resource_group != reosurce_group):
            logger.debug ("Host group %s does not match resource group setting %s", host_group.resource_group,reosurce_group)
            continue
        for host_id, host in host_group.host_list.items():
            if faultDomain and faultDomain != host.fault_domain:
                logger.debug ("Host  %s does not fault domain parameter %s", host.id,faultDomain)
                continue
            host_ranking = host.rank_allocation (vm_size)
            if host_ranking >0:
                candidate_host_dictionary[host.id]=host_ranking
    
    if len(candidate_host_dictionary) == 0:
        logger.debug ("No hosts are available for this VM size")
    else:
        best_host = Host()
        best_rank = 0.0
        for host, ranking in candidate_host_dictionary.items():
            if ranking > best_rank:
                best_host = host
                best_rank = ranking
                logger.debug ("found new candidate. Rank %d, HostId %s", best_rank, best_host)
                        
        logger.debug ("\n\nBest Host is %s", best_host)
        return best_host


def create_host (access_token, subscription_id, location, zone, sku, reosurce_group, host_group, host_name, host_count):
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
    if  location is None or zone is None or sku is None or reosurce_group is None or host_group is None:
        logger.warn ("create_host: Mandatory parameters are location, zone, resource_group, host_group")
        sys.exit()
    if sku not in SKUS.host_skus:
        logger.warn ("create_host: unsupported host sku %s", sku)
        sys.exit()
    if host_name is None:
        host_name = host_group + uuid.uuid1().urn[-6:]


if __name__ == "__main__":
    main()
