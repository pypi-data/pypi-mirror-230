from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import VirtualMachine, HardwareProfile, OSProfile, LinuxConfiguration

class AzureResourceManager:
    def __init__(self, subscription_id):
        self.subscription_id = subscription_id
        self.credentials = DefaultAzureCredential()
        self.compute_client = ComputeManagementClient(self.credentials, self.subscription_id)

    def create_vm(self, vm_name, resource_group_name, location):
        try:
            # Define VM configuration
            vm = VirtualMachine(
                location=location,
                os_profile=OSProfile(computer_name=vm_name, admin_username="adminusername", admin_password="AdminPassword123!"),
                hardware_profile=HardwareProfile(vm_size="Standard_D2s_v3"),
                storage_profile=None,  # Customize storage options as needed
                os_type="linux",
                linux_configuration=LinuxConfiguration(disable_password_authentication=False),
            )

            # Create the VM
            async_vm_creation = self.compute_client.virtual_machines.create_or_update(resource_group_name, vm_name, vm)
            async_vm_creation.wait()
            
            print(f"Azure VM '{vm_name}' created in resource group '{resource_group_name}'")
            return vm_name
        except Exception as e:
            print(f"Error creating Azure VM: {str(e)}")
            return None
    
    def update_vm(self, vm_name, resource_group_name, new_vm_size):
        try:
            vm = self.compute_client.virtual_machines.get(resource_group_name, vm_name)
            vm.hardware_profile.vm_size = new_vm_size
            self.compute_client.virtual_machines.create_or_update(resource_group_name, vm_name, vm)
            print(f"Azure VM '{vm_name}' updated with VM size: {new_vm_size}")
        except Exception as e:
            print(f"Error updating Azure VM: {str(e)}")
    
    def delete_vm(self, vm_name, resource_group_name):
        try:
            async_vm_deletion = self.compute_client.virtual_machines.begin_delete(resource_group_name, vm_name)
            async_vm_deletion.result()
            print(f"Azure VM '{vm_name}' deleted from resource group '{resource_group_name}'")
        except Exception as e:
            print(f"Error deleting Azure VM: {str(e)}")
    
    def read_vm(self, vm_name, resource_group_name):
        try:
            vm = self.compute_client.virtual_machines.get(resource_group_name, vm_name)
            return vm
        except Exception as e:
            print(f"Error reading Azure VM: {str(e)}")
            return None
