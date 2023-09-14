import unittest
from cloudprovider.aws import AWSResourceManager
from cloudprovider.azure import AzureResourceManager

class TestCloudResourceManagement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize AWS and Azure resource managers
        cls.aws_manager = AWSResourceManager(region='us-east-1',aws_access='AKIA5YTNS4S5EL3KLBNU',aws_secret='7hYjzvyEs5UIkxXBVFytilnmEztY+Z2A6+ZQ8fWk')
        # cls.azure_manager = AzureResourceManager(subscription_id='your-subscription-id')

    def test_aws_instance_lifecycle(self):
        # Test AWS EC2 instance creation
        instance_name = 'my-aws-instance'
        instance_id = self.aws_manager.create_instance(instance_name)
        self.assertIsNotNone(instance_id)

        # Test AWS EC2 instance update
        new_instance_type = 't2.small'
        self.aws_manager.update_instance(instance_id, new_instance_type)
        updated_instance = self.aws_manager.read_instance(instance_id)
        self.assertEqual(updated_instance['InstanceType'], new_instance_type)

        # Test AWS EC2 instance termination
        self.aws_manager.terminate_instance(instance_id)
        terminated_instance = self.aws_manager.read_instance(instance_id)
        self.assertIsNone(terminated_instance)

    # def test_azure_vm_lifecycle(self):
    #     # Test Azure VM creation
    #     vm_name = 'my-azure-vm'
    #     resource_group_name = 'my-resource-group'
    #     location = 'eastus'
    #     created_vm_name = self.azure_manager.create_vm(vm_name, resource_group_name, location)
    #     self.assertEqual(created_vm_name, vm_name)

    #     # Test Azure VM update
    #     new_vm_size = 'Standard_DS2_v2'
    #     self.azure_manager.update_vm(vm_name, resource_group_name, new_vm_size)
    #     updated_vm = self.azure_manager.read_vm(vm_name, resource_group_name)
    #     self.assertEqual(updated_vm.hardware_profile.vm_size, new_vm_size)

    #     # Test Azure VM deletion
    #     self.azure_manager.delete_vm(vm_name, resource_group_name)
    #     deleted_vm = self.azure_manager.read_vm(vm_name, resource_group_name)
    #     self.assertIsNone(deleted_vm)

if __name__ == '__main__':
    unittest.main()
