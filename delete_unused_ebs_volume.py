import boto3
from pprint import pprint
import dotenv
import os

# load the environment variables
dotenv.load_dotenv()

# create boto3 client for ec2
client = boto3.client('ec2',
                      region_name=os.getenv('AWS_REGION'),
                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

# create a list where the volume ids of unused volumes will be stored
volumes_to_delete = list()

# call describe_volumes() method of client to get the details of all ebs volumes in given region
# if you have large number of volumes then get the volume detail in batch by using nextToken and process accordingly
volume_detail = client.describe_volumes()

# process each volume in volume_detail
if volume_detail['ResponseMetadata']['HTTPStatusCode'] == 200:
    for each_volume in volume_detail['Volumes']:
        # some logging to make things clear about the volumes in your existing system
        print("Working for volume with volume_id: ", each_volume['VolumeId'])
        print("State of volume: ", each_volume['State'])
        print("Attachment state length: ", len(each_volume['Attachments']))
        print(each_volume['Attachments'])
        print("--------------------------------------------")
        # figuring out the unused volumes
        # the volumes which do not have 'Attachments' key and their state is 'available' is considered to be unused
        if len(each_volume['Attachments']) == 0 and each_volume['State'] == 'available':
            volumes_to_delete.append(each_volume['VolumeId'])

# these are the candidates to be deleted by maintaining waiters for them
pprint(volumes_to_delete)

# proceed for deletion
for each_volume_id in volumes_to_delete:
    try:
        print("Deleting Volume with volume_id: " + each_volume_id)
        response = client.delete_volume(
            VolumeId=each_volume_id
        )
    except Exception as e:
        print("Issue in deleting volume with id: " + each_volume_id + "and error is: " + str(e))

# waiters to verify deletion and keep alive deletion process until completed
waiter = client.get_waiter('volume_deleted')
try:
    waiter.wait(
        VolumeIds=volumes_to_delete,
    )
    print("Successfully deleted all volumes")
except Exception as e:
    print("Error in process with error being: " + str(e))

