import boto3

class AWSResourceManager:
    def __init__(self, region,aws_access,aws_secret):
        self.region = region
        self.aws_access=aws_access
        self.aws_secret=aws_secret
        self.ec2 = self._configure_aws_credentials(region)

    def _configure_aws_credentials(self, region):
        try:
            session = boto3.Session(
                region_name=region,
                aws_access_key_id=self.aws_access,
                aws_secret_access_key=self.aws_secret,
                aws_session_token=None  # If using temporary session credentials
            )
            ec2_client = session.client('ec2')
            return ec2_client
        except Exception as e:
            print(f"Error configuring AWS credentials: {str(e)}")
            return None

    def create_instance(self, instance_name):
        try:
            response = self.ec2.run_instances(
                ImageId='ami-053b0d53c279acc90',  # Replace with a valid AMI ID
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

    def update_instance(self, instance_id, new_instance_type):
        try:
            self.ec2.modify_instance_attribute(
                InstanceId=instance_id,
                InstanceType={'Value': new_instance_type}
            )
            print(f"EC2 instance {instance_id} updated with instance type: {new_instance_type}")
        except Exception as e:
            print(f"Error updating EC2 instance: {str(e)}")

    def read_instance(self, instance_id):
        try:
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            if 'Reservations' in response and response['Reservations']:
                instance = response['Reservations'][0]['Instances'][0]
                return instance
            else:
                print(f"EC2 instance {instance_id} not found.")
                return None
        except Exception as e:
            print(f"Error reading EC2 instance: {str(e)}")
            return None
