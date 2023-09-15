import boto3
import os

class AWSResourceManager:
    def __init__(self):
        try:
            self.region = os.environ.get('AWS_REGION')
        except Exception as e:
            print(f"Error getting AWS region: {str(e)}")
            return None
        self.aws_access=os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret=os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.configure = self._configure_aws_credentials(self.region)
        self.s3 = self._configure_s3_client(self.region)
        self.rds = self._configure_rds_client(self.region)
        self.ec2 = self._configure_ec2_resource(self.region)

    def _configure_aws_credentials(self, region):
        try:
            session = boto3.Session(
                region_name=region,
                aws_access_key_id=self.aws_access,
                aws_secret_access_key=self.aws_secret,
                aws_session_token=None  # If using temporary session credentials
            )
            return True
        except Exception as e:
            print(f"Error configuring AWS credentials: {str(e)}")
            return None
    
    def _configure_s3_client(self, region):
        try:
            s3_client = boto3.client('s3', region_name=region)
            return s3_client
        except Exception as e:
            print(f"Error configuring S3 client: {str(e)}")
            return None
        
    def _configure_rds_client(self, region):
        try:
            rds_client = boto3.client('rds', region_name=region)
            return rds_client
        except Exception as e:
            print(f"Error configuring RDS client: {str(e)}")
            return None
    
    def _configure_ec2_resource(self, region):
        try:
            ec2_resource = boto3.resource('ec2', region_name=region)
            return ec2_resource
        except Exception as e:
            print(f"Error configuring EC2 resource: {str(e)}")
            return None

    def create_instance(self, instance_name, instance_type, ami_id):
        try:
            response = self.ec2.run_instances(
                ImageId=ami_id,
                InstanceType=instance_type,
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
            print(f"EC2 instance '{instance_name}' created with ID: {instance_id}")
            return instance_id
        except Exception as e:
            print(f"Error creating EC2 instance: {str(e)}")
            return None    
    
    def list_amis(self):
        try:
            # List all AMIs in the region
            response = self.ec2.describe_images(Owners=['self'])
            amis = response.get('Images', [])
            for ami in amis:
                print(f"AMI Name: {ami['Name']}, ID: {ami['ImageId']}")
            return amis
        except Exception as e:
            print(f"Error listing AMIs: {str(e)}")
            return []

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
    
    def create_s3_bucket(self, bucket_name):
        try:
            self.s3.create_bucket(Bucket=bucket_name)
            print(f"AWS S3 bucket '{bucket_name}' created")
        except Exception as e:
            print(f"Error creating S3 bucket: {str(e)}")
    
    def upload_file_to_s3(self, bucket_name, file_path, object_name):
        try:
            self.s3.upload_file(file_path, bucket_name, object_name)
            print(f"Uploaded file '{object_name}' to S3 bucket '{bucket_name}'")
        except Exception as e:
            print(f"Error uploading file to S3: {str(e)}")
    
    def list_objects_in_s3_bucket(self, bucket_name):
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name)
            objects = response.get('Contents', [])
            for obj in objects:
                print(f"Object: {obj['Key']}")
        except Exception as e:
            print(f"Error listing objects in S3 bucket: {str(e)}")
    
    def delete_object_from_s3_bucket(self, bucket_name, object_name):
        try:
            self.s3.delete_object(Bucket=bucket_name, Key=object_name)
            print(f"Deleted object '{object_name}' from S3 bucket '{bucket_name}'")
        except Exception as e:
            print(f"Error deleting object from S3 bucket: {str(e)}")

    def delete_s3_bucket(self, bucket_name):
        try:
            self.s3.delete_bucket(Bucket=bucket_name)
            print(f"Deleted S3 bucket '{bucket_name}'")
        except Exception as e:
            print(f"Error deleting S3 bucket: {str(e)}")

    def create_rds_instance(self, db_instance_identifier, db_instance_class, db_name, username, password):
        try:
            response = self.rds.create_db_instance(
                DBInstanceIdentifier=db_instance_identifier,
                AllocatedStorage=20,
                DBInstanceClass=db_instance_class,
                Engine='mysql',
                MasterUsername=username,
                MasterUserPassword=password,
                DBName=db_name,
                VPCSecurityGroups=['default'],  # Update with your security group IDs
                AvailabilityZone=self.region + 'a',
            )
            print(f"AWS RDS instance '{db_instance_identifier}' created")
            return db_instance_identifier
        except Exception as e:
            print(f"Error creating RDS instance: {str(e)}")
            return None
    
    def list_rds_instances(self):
        try:
            response = self.rds.describe_db_instances()
            instances = response.get('DBInstances', [])
            for instance in instances:
                print(f"RDS Instance: {instance['DBInstanceIdentifier']}")
        except Exception as e:
            print(f"Error listing RDS instances: {str(e)}")

    def delete_rds_instance(self, db_instance_identifier):
        try:
            self.rds.delete_db_instance(
                DBInstanceIdentifier=db_instance_identifier,
                SkipFinalSnapshot=True,
            )
            print(f"Deleted RDS instance '{db_instance_identifier}'")
        except Exception as e:
            print(f"Error deleting RDS instance: {str(e)}")
    
    
