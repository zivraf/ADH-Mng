'''dh_crud.py - basic dedicated hosts operations'''
import json
import sys

import azurerm
import logging

log_format = " %(asctime)s [%(levelname)s] %(message)s"
logger = logging.getLogger('example')
logging.basicConfig(format=log_format, level=logging.DEBUG)

class SKUS:
    vm_skus = {"Standard_D2s_v3":{"cpu_count":2,"hyper_threading":2,"mem_size":8}, \
        "Standard_D4s_v3":{"cpu_count":4,"hyper_threading":2,"mem_size":16}, \
        "Standard_D8s_v3":{"cpu_count":8,"hyper_threading":2,"mem_size":32}, \
        "Standard_D16s_v3":{"cpu_count":16,"hyper_threading":2,"mem_size":64}, \
        "Standard_D32s_v3":{"cpu_count":32,"hyper_threading":2,"mem_size":128}, \
        "Standard_D64s_v3":{"cpu_count":64,"hyper_threading":2,"mem_size":256}, \
        "Standard_E2s_v3":{"cpu_count":2,"hyper_threading":2,"mem_size":16}, \
        "Standard_E4s_v3":{"cpu_count":4,"hyper_threading":2,"mem_size":32}, \
        "Standard_E8s_v3":{"cpu_count":8,"hyper_threading":2,"mem_size":64}, \
        "Standard_E16s_v3":{"cpu_count":16,"hyper_threading":2,"mem_size":128}, \
        "Standard_E32s_v3":{"cpu_count":32,"hyper_threading":2,"mem_size":256}, \
        "Standard_E64s_v3":{"cpu_count":64,"hyper_threading":2,"mem_size":432} \
             }
    host_skus = {"DSv3-Type1":{"core_count":64,"mem_size":440}, \
                 "DSv3-Type2":{"core_count":64,"mem_size":640},
                 "ESv3-Type1":{"core_count":64,"mem_size":440},
                 "FSv2-Type2":{"core_count":72,"mem_size":440}, }

    host_sku_to_vm_skus = {"DSv3-Type1":{"Standard_D2s_v3","Standard_D4s_v3","Standard_D8s_v3", \
        "Standard_D16s_v3","Standard_D32s_v3","Standard_D64s_v3"}, \
        "DSv3-Type2":{"Standard_D2s_v3","Standard_D4s_v3","Standard_D8s_v3", \
        "Standard_D16s_v3","Standard_D32s_v3","Standard_D64s_v3"} , \
        "ESv3-Type1":{"Standard_E2s_v3","Standard_E4s_v3","Standard_E8s_v3", \
        "Standard_E16s_v3","Standard_E32s_v3","Standard_E64s_v3"} , \
        "ESv3-Type2":{"Standard_E2s_v3","Standard_E4s_v3","Standard_E8s_v3", \
        "Standard_E16s_v3","Standard_E32s_v3","Standard_E64s_v3"},
        "FSv2-Type2":{"Standard_F2s_v2","Standard_F4s_v2","Standard_F8s_v2", \
        "Standard_F16s_v2","Standard_F32s_v2","Standard_F64s_v2"} } 

class VM:
    def __init__(self):            
        self.name = ""
        self.id = ""
        self.size = ""
        # calculated host attributes
        self.core_count = 0
        self.mem_size = 0 
        self.hyper_threading_ratio = 1

    def init (self,vm_obj):
        print ("TBD")

    def populate_vm (self, curr_vm):
        '''Populate VM date as retrived from GET on Microsoft.Compute/VirtualMachine
            Args:
                curr_vm (str): VM Object representation
        '''
        self.name = curr_vm['name']
        self.id = curr_vm['id']
        self.size = curr_vm['properties']['hardwareProfile']['vmSize']
        # calculated host attributes
        self.core_count = 0
        self.mem_size = 0 
        self.hyper_threading_ratio = 1
        

class Host:
    def __init__(self):            
        self.name = ""
        self.group_name = ""
        self.location = ""
        self.id = ""
        self.sku = ""
        self.vm_list = {}
        self.fault_domain = ""

        # calculated host attributes
        self.total_cores = 0
        self.total_mem = 0
        self.utilized_cores =0
        self.utilized_mem = 0 
        self.available_cores = 0
        self.available_mem =0
    
    def calculate_utilization(self):
        '''Calculate the utilization of the host. Fill in the host size and then iterate all hosted VMs to calculate utilization. 
        '''
        # logger.debug ("dedicated_host: calculate_utilization:Enter")
        self.utilized_cores = 0
        self.utilized_mem = 0 
        if (self.total_cores == 0 or self.total_mem == 0):
            self.total_cores = SKUS.host_skus[self.sku]["core_count"]
            self.total_mem = SKUS.host_skus[self.sku]["mem_size"]
        
        for vm_name, vm in self.vm_list.items():
            if vm.size:
                vm.core_count = SKUS.vm_skus[vm.size]["cpu_count"]
                self.utilized_cores += vm.core_count
                vm.mem_size = SKUS.vm_skus[vm.size]["mem_size"]
                self.utilized_mem += vm.mem_size
        
        self.available_cores=self.total_cores - self.utilized_cores
        self.available_mem = self.total_mem - self.utilized_mem
        
        logger.debug ("DedicatedHost: %s, group %s, %s, FD: %s ,%d VMs, Utilization(used/total): Cores %d / %d; Mem %d / %d", \
            self.name,self.group_name, self.sku, self.fault_domain, len(self.vm_list), self.utilized_cores, self.total_cores,self.utilized_mem, self.total_mem)
    
    def rank_allocation(self,vm_size):
        vm_size_list = SKUS.host_sku_to_vm_skus[self.sku]
        if vm_size not in SKUS.host_sku_to_vm_skus[self.sku]:
            # not a supported size for family
            return 0.0
        req_cores = SKUS.vm_skus[vm_size]["cpu_count"]
        req_mem = SKUS.vm_skus[vm_size]["mem_size"]
        if req_cores>self.available_cores or req_mem>self.available_mem:
            # no room in the host
            return 0.0
        return  max (req_cores/self.available_cores , req_mem/self.available_mem)        

   
    def populate_host (self, curr_host, dhg_name):
        '''Populate a dedicated host with host object including VM IDs
            Args:
                curr_host (str): Dedicated Host JSON object 
        '''
        self.name = curr_host['name']
        self.sku = curr_host['sku']['name']
        self.location = curr_host['location']
        self.id = curr_host['id']
        self.group_name = dhg_name
        if 'faultDomain' in curr_host['properties']:
            self.fault_domain = curr_host['properties']['faultDomain']
        for curr_vm in curr_host['properties']['virtualMachines']:
            vm = VM()
            vm.id = curr_vm['id'].upper()
            self.vm_list[vm.id]=vm
            # logger.debug ("populate a VM %s",vm.id)

    def init(self,host_obj):
        print ("TBD")



class HostGroup:
    def __init__(self):            
        self.id =""
        self.resource_group = ""
        self.name = ""
        self.location = ""
        self.az = ""
        self.host_list = {}

    def populate_host_group(self, dhg,access_token, subscription_id,resource_group):
        # logger.debug ("HostGroup:populate_cache")
        self.name = dhg['name']
        self.location = dhg['location']
        self.id = dhg['id']
        if dhg['zones']:
            self.az= dhg['zones'][0]   
        
        resource_id = dhg['id'].split("/")
        self.resource_group =(resource_id[4])
        hosts_json = azurerm.list_dh(access_token, subscription_id,self.resource_group,dhg['name'])    
            
        logger.debug ("HostGroup:%s, Location %s, AZ %s,  %s with %d hosts", self.name, self.location, self.az,self.id, len(hosts_json['value']))
        for curr_host in hosts_json['value']:
            dh = Host()
            dh.populate_host (curr_host, self.name)
            self.host_list[dh.name]= dh

         



class DedicateHostCache:
    def __init__(self):            
        self.host_group_list = {}

    def populate_host_groups (self, dhgList,access_token, subscription_id, resource_group):
        # logger.debug ("DedicateHosthost_groups:populate_cache")
        
        for curr_dhg in dhgList['value']:
            logger.debug("Iterating DHG "+curr_dhg['name'])
            dhg = HostGroup()
            dhg.populate_host_group(curr_dhg,access_token, subscription_id,resource_group)
            self.host_group_list[curr_dhg['id']] = dhg

    def update_vm_info (self,vm_list):
            # logger.debug ("DedicateHosthost_groups:update_vm_info")
            for host_group_id, host_group in self.host_group_list.items():
                for host_id, host in host_group.host_list.items():
                    for vm_id, vm in host.vm_list.items():
                        if vm_id in vm_list:
                            vm.populate_vm (vm_list[vm_id])
                    host.calculate_utilization()
                        

    
