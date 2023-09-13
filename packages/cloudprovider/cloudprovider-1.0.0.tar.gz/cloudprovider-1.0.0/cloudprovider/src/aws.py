import boto3

class AWSResourceManager:
    def __init__(self, region):
        self.region = region
        self.ec2 = boto3.client('ec2', region_name=self.region)

    def create_instance(self, instance_name):
        try:
            response = self.ec2.run_instances(
                ImageId='ami-0a0c8eebcdd6dcbd0',  # Replace with a valid AMI ID
                InstanceType='t2.micro',
                MinCount=1,
                MaxCount=1,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': instance_name
                            },
                        ]
                    },
                ]
            )
            instance_id = response['Instances'][0]['InstanceId']
            return instance_id
        except Exception as e:
            print(f"Error creating EC2 instance: {str(e)}")
            return None

    def terminate_instance(self, instance_id):
        try:
            self.ec2.terminate_instances(InstanceIds=[instance_id])
            print(f"EC2 instance {instance_id} terminated")
        except Exception as e:
            print(f"Error terminating EC2 instance: {str(e)}")
